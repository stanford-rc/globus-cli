from globus_cli.parser import GlobusCLISharedParser
from globus_cli.helpers import supports_additional_params

from globus_sdk import AuthClient


def add_subcommand_parsers(subparsers):
    """
    Add Globus Auth commands
    """
    auth_parser = subparsers.add_parser(
        'auth', help=(
            'Interact with Globus Auth API. '
            'Used to inspect tokens, identities, identity sets, '
            'consent to service terms, revoke and manage consents, '
            'manage OAuth Clients, and a variety of other '
            'Authorization and Authentication based activities.'))

    subsubparsers = auth_parser.add_subparsers(
        title='Commands', parser_class=GlobusCLISharedParser, metavar='')

    add_get_identities_parser(subsubparsers)
    add_token_introspect_parser(subsubparsers)


def add_get_identities_parser(subsubparsers):
    """
    Subcommand parser for `globus auth get-identities`
    """
    get_identities_parser = subsubparsers.add_parser(
        'get-identities', help=(
            'Inspect Globus Auth Identities')
        )
    get_identities_parser.set_defaults(func=get_identities)

    get_identities_parser.add_argument(
        '--usernames', dest='usernames', default=[], nargs='+',
        help='Usernames to lookup in Globus Auth')

    get_identities_parser.add_argument(
        '--identities', dest='identities', default=[], nargs='+',
        help='Identity IDs to lookup in Globus Auth')


def add_token_introspect_parser(subsubparsers):
    """
    Subcommand parser for `globus auth token-introspect`
    TODO: implement me
    """
    token_introspect_parser = subsubparsers.add_parser(
        'token-introspect', help=(
            'Inspect Globus Auth Token')
        )
    token_introspect_parser.set_defaults(func=token_introspect)

    token_introspect_parser.add_argument(
        'token', help='Token to lookup in Globus Auth')


@supports_additional_params
def get_identities(args):
    """
    Executor for `globus auth get-identities`
    """
    client = AuthClient()

    # copy the additional params we are given
    params = dict(args.additional_params)

    # set commandline params if passed
    if args.usernames:
        params['usernames'] = ','.join(args.usernames)
    if args.identities:
        params['ids'] = ','.join(args.usernames)

    res = client.get_identities(**params)

    print(res.text_body)


@supports_additional_params
def token_introspect(args):
    """
    Executor for `globus auth token-introspect`
    """
    raise NotImplementedError('Requires Client Credential Support')
    """
    client = AuthClient()

    # copy the additional params we are given
    params = dict(args.additional_params)

    token = config.get_auth_token(client.environment)

    res = client.token_introspect(token, **params)

    print(res.text_body)
    """
