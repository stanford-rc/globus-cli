import click

from globus_cli.safeio import safeprint
from globus_cli.helpers import common_options
from globus_cli.config import (
    AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME,
    internal_auth_client, write_option)


@click.command('login',
               short_help=('Login to Globus to get credentials for '
                           'the Globus CLI'),
               help=('Get credentials for the Globus CLI. '
                     'Necessary before any Globus CLI commands which require '
                     'authentication will work'))
@common_options
def login_command():
    # build the NativeApp client object
    ac = internal_auth_client()

    # and do the Native App Grant flow
    ac.oauth2_start_flow_native_app(refresh_tokens=True)

    # prompt
    linkprompt = 'Please login to Globus here'
    safeprint('{0}:\n{1}\n{2}\n{1}\n'
              .format(linkprompt, '-'*len(linkprompt),
                      ac.oauth2_get_authorize_url()))

    # come back with auth code
    auth_code = click.prompt(
        'Enter the resulting Authorization Code here')

    # exchange, done!
    tkn = ac.oauth2_exchange_code_for_tokens(auth_code)

    # extract access tokens from final response
    transfer_at = (
        tkn.by_resource_server['transfer.api.globus.org']['access_token'])
    transfer_rt = (
        tkn.by_resource_server['transfer.api.globus.org']['refresh_token'])
    auth_at = (
        tkn.by_resource_server['auth.globus.org']['access_token'])
    auth_rt = (
        tkn.by_resource_server['auth.globus.org']['refresh_token'])

    # write data to config
    # TODO: remove once we deprecate these fully
    write_option('transfer_token', transfer_at, section='general')
    write_option('auth_token', auth_at, section='general')
    # new values we want to use moving forward
    write_option(TRANSFER_RT_OPTNAME, transfer_rt)
    write_option(AUTH_RT_OPTNAME, auth_rt)
