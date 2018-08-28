import click

from globus_sdk.exc import AuthAPIError
from globus_cli.helpers import (
    is_remote_session, do_link_auth_flow, do_local_server_auth_flow)
from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, no_local_server_option
from globus_cli.config import (
    AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME, internal_auth_client, lookup_option)

_SHARED_EPILOG = ("""\

You can check your primary identity with
  globus whoami

For information on which of your identities are in session use
  globus session show

Logout of the Globus CLI with
  globus logout
""")

_LOGIN_EPILOG = (u"""\

You have successfully logged in to the Globus CLI!
""") + _SHARED_EPILOG

_LOGGED_IN_RESPONSE = ("""\
You are already logged in!

You may force a new login with
  globus login --force
""") + _SHARED_EPILOG


@click.command('login',
               short_help=('Log into Globus to get credentials for '
                           'the Globus CLI'),
               help=('Get credentials for the Globus CLI. '
                     'Necessary before any Globus CLI commands which require '
                     'authentication will work'))
@common_options(no_format_option=True, no_map_http_status_option=True)
@no_local_server_option
@click.option('--force', is_flag=True,
              help=('Do a fresh login, ignoring any existing credentials'))
def login_command(no_local_server, force):
    # if not forcing, stop if user already logged in
    if not force and check_logged_in():
        safeprint(_LOGGED_IN_RESPONSE)
        return

    # use a link login if remote session or user requested
    if no_local_server or is_remote_session():
        do_link_auth_flow(force_new_client=True)

    # otherwise default to a local server login flow
    else:
        safeprint(
            "You are running 'globus login', which should automatically open "
            "a browser window for you to login.\n"
            "If this fails or you experience difficulty, try "
            "'globus login --no-local-server'"
            "\n---")
        do_local_server_auth_flow(force_new_client=True)

    # print epilog
    safeprint(_LOGIN_EPILOG)


def check_logged_in():
    # first, try to get the refresh tokens from config
    # we can skip the access tokens and their expiration times as those are not
    # strictly necessary
    transfer_rt = lookup_option(TRANSFER_RT_OPTNAME)
    auth_rt = lookup_option(AUTH_RT_OPTNAME)

    # if either of the refresh tokens are null return False
    if (transfer_rt is None or auth_rt is None):
        return False

    # get or create the instance client
    auth_client = internal_auth_client(requires_instance=True)

    # check that tokens and client are valid
    try:
        for tok in (transfer_rt, auth_rt):
            res = auth_client.oauth2_validate_token(tok)
            if not res['active']:
                return False

    # if the instance client is invalid, an AuthAPIError will be raised
    # we then force a new client to be created before continuing
    except AuthAPIError:
        return False

    return True
