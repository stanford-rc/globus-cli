from globus_cli.helpers import (
    cliargs, CLIArg, print_json_response, outformat_is_json,
    text_header_and_format)
from globus_cli.services.auth.helpers import get_auth_client


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

    if outformat_is_json(args):
        print_json_response(res)
    else:
        ids = res['identities']

        def max_keylen(key):
            return max(len(i[key]) for i in ids)

        max_fullname_len = max_keylen('name')
        max_username_len = max_keylen('username')
        max_org_len = max_keylen('organization')
        max_email_len = max_keylen('email')

        text_col_format = text_header_and_format(
            [(36, 'ID'),
             (max_fullname_len, 'Full Name'),
             (max_username_len, 'Username'),
             (max_org_len, 'Organization'),
             (max_email_len, 'Email Address')])
        for identity in ids:
            print(text_col_format.format(
                identity['id'], identity['name'], identity['username'],
                identity['organization'], identity['email']))
