import json
from globus_sdk import AuthClient

from globus_cli import version
from globus_cli.helpers import cliargs, CLIArg, is_valid_identity_name


def get_auth_client():
    client = AuthClient(app_name=version.app_name)
    return client


def _lookup_identity_field(id_name=None, id_id=None, field='id'):
    assert (id_name or id_id) and not (id_name and id_id)
    client = get_auth_client()

    if id_name:
        kw = {'usernames': id_name}
    else:
        kw = {'ids': id_id}

    return client.get_identities(**kw)['identities'][0][field]


def maybe_lookup_identity_id(identity_name):
    if is_valid_identity_name:
        return _lookup_identity_field(id_name=identity_name)
    else:
        return identity_name


def lookup_identity_name(identity_id):
    return _lookup_identity_field(id_id=identity_id, field='username')


def _validate_get_identities_args(args, parser):
    if args.usernames == [] and args.identities == []:
        parser.error('get-identities requires either --usernames or '
                     '--identities')


@cliargs('Inspect Globus Auth Identities',
         CLIArg('usernames', default=[], nargs='+',
                help='Usernames to lookup in Globus Auth'),
         CLIArg('identities', default=[], nargs='+',
                help='Identity IDs to lookup in Globus Auth'),
         arg_validator=_validate_get_identities_args)
def get_identities(args):
    """
    Executor for `globus auth get-identities`
    """
    client = get_auth_client()

    params = {}

    # set commandline params if passed
    if args.usernames:
        params['usernames'] = ','.join(args.usernames)
    if args.identities:
        params['ids'] = ','.join(args.usernames)

    res = client.get_identities(**params)

    print(json.dumps(res.data, indent=2))


@cliargs('Inspect Globus Auth Tokens',
         CLIArg('token', help='Token to lookup in Globus Auth'))
def token_introspect(args):
    """
    Executor for `globus auth token-introspect`
    """
    # client.token_introspect(token, **params)
    raise NotImplementedError('Requires Client Credential Support')
