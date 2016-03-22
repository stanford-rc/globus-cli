from globus_sdk import AuthClient

import json


def get_identities(args):
    """
    Executor for `globus auth get-identities`
    """
    client = AuthClient()

    params = {}

    # set commandline params if passed
    if args.usernames:
        params['usernames'] = ','.join(args.usernames)
    if args.identities:
        params['ids'] = ','.join(args.usernames)

    res = client.get_identities(**params)

    print(json.dumps(res.data, indent=2))


def token_introspect(args):
    """
    Executor for `globus auth token-introspect`
    """
    raise NotImplementedError('Requires Client Credential Support')
    """
    client = AuthClient()

    params = {}

    token = config.get_auth_token(client.environment)

    res = client.token_introspect(token, **params)

    print(res.text_body)
    """
