from globus_cli.helpers import fill_delegate_proxy_activation_requirements
from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import PUBLIC_KEY


class DelegateProxyTests(CliTestCase):
    def test_fill_delegate_proxy_activation_requirements(self):
        """
        Uses the public key from constants to form a fake activation
        requirements response, and an expired proxy to test
        fill_delegate_proxy_activation_requirements.
        """
        # file containing an expired x509 from a myproxy-logon
        x509 = "tests/framework/files/cert.pem"

        activation_requirements = {
            "DATA_TYPE": "activation_requirements",
            "DATA": [
                {
                    "DATA_TYPE": "activation_requirement",
                    "type": "delegate_proxy",
                    "name": "public_key",
                    "value": PUBLIC_KEY,
                },
                {
                    "DATA_TYPE": "activation_requirement",
                    "type": "delegate_proxy",
                    "name": "proxy_chain",
                    "value": None,
                },
            ],
        }

        filled_requirements = fill_delegate_proxy_activation_requirements(
            activation_requirements, x509
        )

        # assert the proxy_chain now contains a certificate
        self.assertIn(
            "-----BEGIN CERTIFICATE-----", filled_requirements["DATA"][1]["value"]
        )
        self.assertIn(
            "-----END CERTIFICATE-----", filled_requirements["DATA"][1]["value"]
        )

    def test_bad_x509(self):
        """
        Uses the public key from constants to form a fake activation
        requirements response, then attempts to fill the activation
        requirements with bad x509 files. Confirms value errors
        """
        activation_requirements = {
            "DATA_TYPE": "activation_requirements",
            "DATA": [
                {
                    "DATA_TYPE": "activation_requirement",
                    "type": "delegate_proxy",
                    "name": "public_key",
                    "value": PUBLIC_KEY,
                },
                {
                    "DATA_TYPE": "activation_requirement",
                    "type": "delegate_proxy",
                    "name": "proxy_chain",
                    "value": None,
                },
            ],
        }

        # no file
        with self.assertRaises(IOError) as err:
            fill_delegate_proxy_activation_requirements(
                activation_requirements, "nosuchfile.pem"
            )
        self.assertIn("No such file", str(err.exception))

        # non pem file
        with self.assertRaises(ValueError) as err:
            fill_delegate_proxy_activation_requirements(
                activation_requirements, "tests/framework/constants.py"
            )
        self.assertIn("Unable to parse PEM data", str(err.exception))

        # no private key
        with self.assertRaises(ValueError) as err:
            fill_delegate_proxy_activation_requirements(
                activation_requirements, "tests/framework/files/no_key.pem"
            )
        self.assertIn("Failed to decode PEM data", str(err.exception))

        # only private key
        with self.assertRaises(ValueError) as err:
            fill_delegate_proxy_activation_requirements(
                activation_requirements, "tests/framework/files/no_cert.pem"
            )
        self.assertIn("Unable to parse PEM data", str(err.exception))
