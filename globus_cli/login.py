import click

from globus_cli.safeio import safeprint
from globus_cli.helpers import common_options
from globus_cli.config import get_internal_auth_client

# FIXME: extract this helper from the config commands or move `globus login`
# into the config commands
from globus_cli.config_command.helpers import load_config


@click.command('login',
               short_help=('Login to Globus to get credentials for '
                           'the Globus CLI'),
               help=('Get credentials for the Globus CLI. '
                     'Necessary before any Globus CLI commands which require '
                     'authentication will work'))
@common_options
def login_command():
    # get the NativeApp client
    ac = get_internal_auth_client()

    # and do the Native App Grant flow
    # FIXME: currently just does ATs, change to RTs
    ac.oauth2_start_flow_native_app()

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

    # extract tokens from final response
    transfer_token = (
        tkn.by_resource_server['transfer.api.globus.org']['access_token'])
    auth_token = (
        tkn.by_resource_server['auth.globus.org']['access_token'])

    # config file as object
    conf = load_config()
    # insert tokens
    conf['general']['transfer_token'] = transfer_token
    conf['general']['auth_token'] = auth_token
    # write to disk
    conf.write()
