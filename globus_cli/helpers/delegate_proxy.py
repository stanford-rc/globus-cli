import struct
import os
import time
try:
    from M2Crypto import X509, RSA, EVP, ASN1, BIO
    m2crypto_imported = True
except ImportError:
    m2crypto_imported = False

_begin_private_key = "-----BEGIN RSA PRIVATE KEY-----"
_end_private_key = "-----END RSA PRIVATE KEY-----"
# The issuer is required to have this bit set if keyUsage is present;
# see RFC 3820 section 3.1.
REQUIRED_KEY_USAGE = ["Digital Signature"]


def fill_delegate_proxy_activation_requirements(requirements_data, cred_file,
                                                lifetime_hours=12):
    """
    Given the activation requirements for an endpoint and a filename for
    X.509 credentials, extracts the public key from the activation
    requirements, uses the key and the credentials to make a proxy credential,
    and returns the requirements data with the proxy chain filled in.
    """

    # cannot proceed without M2Crypto
    if not m2crypto_imported:
        raise ImportError("Unable to import M2Crypto")

    # get the public key from the activation requirements
    for data in requirements_data["DATA"]:
        if data["type"] == "delegate_proxy" and data["name"] == "public_key":
            public_key = data["value"]
            break
    else:
        raise ValueError((
            "No public_key found in activation requirements, this endpoint "
            "does not support Delegate Proxy activation."))

    # get user credentials from user credential file"
    with open(cred_file) as f:
        issuer_cred = f.read()

    # create proxy from the public key and the user credentials
    proxy = create_proxy(
        issuer_cred, public_key, lifetime_hours)

    # return the activation requirements document with the proxy_chain filled
    for data in requirements_data["DATA"]:
        if data["type"] == "delegate_proxy" and data["name"] == "proxy_chain":
            data["value"] = proxy
            return requirements_data
    else:
        raise ValueError((
            "No proxy_chain found in activation requirements, this endpoint "
            "does not support Delegate Proxy activation."))


def create_proxy(issuer_cred, public_key, lifetime_hours):
    old_proxy = False

    # Standard order is cert, private key, then the chain.
    try:
        _begin_idx = issuer_cred.index(_begin_private_key)
        _end_idx = issuer_cred.index(_end_private_key) + len(_end_private_key)
        issuer_key = issuer_cred[_begin_idx:_end_idx]
        issuer_cert = issuer_cred[:_begin_idx]
        issuer_chain = issuer_cert + issuer_cred[_end_idx:]
    except:
        raise ValueError("Unable to find private key in credentials, "
                         "make sure the X.509 is in PEM format.")

    proxy = X509.X509()
    proxy.set_version(2)
    # Under RFC 3820 there are many ways to generate the serial number. However
    # making the number unpredictable has security benefits, e.g. it can make
    # this style of attack more difficult:
    # http://www.win.tue.nl/hashclash/rogue-ca
    serial = struct.unpack("<Q", os.urandom(8))[0]
    proxy.set_serial_number(serial)

    now = int(time.time())
    not_before = ASN1.ASN1_UTCTIME()
    not_before.set_time(now)
    proxy.set_not_before(not_before)

    not_after = ASN1.ASN1_UTCTIME()
    not_after.set_time(now + lifetime_hours * 3600)
    proxy.set_not_after(not_after)

    pkey = EVP.PKey()
    tmp_bio = BIO.MemoryBuffer(str(public_key))
    rsa = RSA.load_pub_key_bio(tmp_bio)
    pkey.assign_rsa(rsa)
    del rsa
    del tmp_bio
    proxy.set_pubkey(pkey)

    try:
        issuer = X509.load_cert_string(issuer_cert)
    except Exception as e:
        raise ValueError(("Error parsing credentials, make sure the X.509 is "
                          "in PEM format: {}".format(e)))

    # Examine the last CN to see if it looks like and old proxy.
    cn_entries = issuer.get_subject().get_entries_by_nid(
                                        X509.X509_Name.nid["CN"])
    if cn_entries:
        last_cn = cn_entries[-1].get_data()
        old_proxy = (str(last_cn) in ("proxy", "limited proxy"))

    # If the issuer has keyUsage extension, make sure it contains all
    # the values we require.
    try:
        keyUsageExt = issuer.get_ext("keyUsage")
        if keyUsageExt:
            values = keyUsageExt.get_value().split(", ")
            for required in REQUIRED_KEY_USAGE:
                if required not in values:
                    raise ValueError(
                      "issuer contains keyUsage without required usage '%s'"
                      % required)
    except LookupError:
        keyUsageExt = None

    # hack to get a copy of the X509 name that we can append to.
    issuer_copy = X509.load_cert_string(issuer_cert)
    proxy_subject = issuer_copy.get_subject()
    if old_proxy:
        proxy_subject.add_entry_by_txt(field="CN", type=ASN1.MBSTRING_ASC,
                                       entry="proxy",
                                       len=-1, loc=-1, set=0)
    else:
        proxy_subject.add_entry_by_txt(field="CN", type=ASN1.MBSTRING_ASC,
                                       entry=str(serial),
                                       len=-1, loc=-1, set=0)
    proxy.set_subject(proxy_subject)
    proxy.set_issuer(issuer.get_subject())

    # create a full proxy (legacy/old or rfc, draft is not supported)
    if old_proxy:
        # For old proxies, there is no spec that defines the interpretation,
        # so the keyUsage extension is more important.
        # TODO: copy extended key usage also?
        if keyUsageExt:
            # Copy from the issuer if it had a keyUsage extension.
            ku_ext = X509.new_extension("keyUsage", keyUsageExt.get_value(), 1)
        else:
            # Otherwise default to this set of usages.
            ku_ext = X509.new_extension(
                "keyUsage",
                "Digital Signature, Key Encipherment, Data Encipherment", 1)
        proxy.add_ext(ku_ext)
    else:
        # For RFC proxies the effictive usage is defined as the intersection
        # of the usage of each cert in the chain. See section 4.2 of RFC 3820.
        # We opt not to add keyUsage.
        pci_ext = X509.new_extension("proxyCertInfo",
                                     "critical,language:Inherit all", 1)
        proxy.add_ext(pci_ext)

    issuer_rsa = RSA.load_key_string(issuer_key)
    sign_pkey = EVP.PKey()
    sign_pkey.assign_rsa(issuer_rsa)
    proxy.sign(pkey=sign_pkey, md="sha1")
    return proxy.as_pem() + issuer_chain
