import re
from globus_sdk import AuthClient, RefreshTokenAuthorizer

from globus_cli import version
from globus_cli.config import (get_auth_tokens, internal_auth_client,
                               set_auth_access_token)

# what qualifies as a valid Identity Name?
_IDENTITY_NAME_REGEX = '^[a-zA-Z0-9]+.*@[a-zA-z0-9-]+\..*[a-zA-Z]+$'


def _update_access_tokens(token_response):
    tokens = token_response.by_resource_server['auth.globus.org']
    set_auth_access_token(tokens['access_token'],
                          tokens['expires_at_seconds'])


def is_valid_identity_name(identity_name):
    """
    Check if a string is a valid identity name.
    Does not do any preprocessing of the identity name, so you must do so
    before invocation.
    """
    if re.match(_IDENTITY_NAME_REGEX, identity_name) is None:
        return False
    else:
        return True


def get_auth_client():
    tokens = get_auth_tokens()
    authorizer = None

    # if there's a refresh token, use it to build the authorizer
    if tokens['refresh_token'] is not None:
        authorizer = RefreshTokenAuthorizer(
            tokens['refresh_token'], internal_auth_client(),
            tokens['access_token'], tokens['access_token_expires'],
            on_refresh=_update_access_tokens)

    client = AuthClient(authorizer=authorizer, app_name=version.app_name)
    return client


def _lookup_identity_field(id_name=None, id_id=None, field='id',
                           provision=False):
    assert (id_name or id_id) and not (id_name and id_id)
    client = get_auth_client()

    kw = dict(provision=provision)
    if id_name:
        kw.update({'usernames': id_name})
    else:
        kw.update({'ids': id_id})

    try:
        return client.get_identities(**kw)['identities'][0][field]
    except (IndexError, KeyError):
        # IndexError: identity does not exist and wasn't provisioned
        # KeyError: `field` does not exist for the requested identity
        return None


def maybe_lookup_identity_id(identity_name, provision=False):
    if is_valid_identity_name(identity_name):
        return _lookup_identity_field(
            id_name=identity_name, provision=provision)
    else:
        return identity_name


def lookup_identity_name(identity_id):
    return _lookup_identity_field(id_id=identity_id, field='username')


class LazyIdentityMap(object):
    """
    There's a common pattern of not needing identity IDs resolved to
    usernames until text output is being rendered.

    Rather than having all of the usage sites explicitly check the output
    format which is going to be used, define a lazy dict-like type which does a
    bulk identity lookup whenever it is first accessed.
    """
    def __init__(self, identity_ids):
        # uniquify and copy
        self.identity_ids = list(set(identity_ids))

        self._resolved_map = None

    def _lookup_identity_names(self):
        """
        Batch resolve identities to usernames.
        Returns a dict mapping IDs to Usernames
        """
        id_batch_size = 100

        # fetch in batches of 100, store in a dict
        ac = get_auth_client()
        self._resolved_map = {}
        for i in range(0, len(self.identity_ids), id_batch_size):
            chunk = self.identity_ids[i:i+id_batch_size]
            resolved_result = ac.get_identities(ids=chunk)
            for x in resolved_result['identities']:
                self._resolved_map[x['id']] = x['username']

    def get(self, *args, **kwargs):
        if self._resolved_map is None:
            self._lookup_identity_names()
        return self._resolved_map.get(*args, **kwargs)
