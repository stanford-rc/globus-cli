import click
from globus_sdk.exc import AuthAPIError

from globus_cli.config import (
    AUTH_RT_OPTNAME,
    TRANSFER_RT_OPTNAME,
    internal_auth_client,
    lookup_option,
)
from globus_cli.helpers import (
    do_link_auth_flow,
    do_local_server_auth_flow,
    is_remote_session,
)
from globus_cli.parsing import command, no_local_server_option

_SHARED_EPILOG = """\

You can check your primary identity with
  globus whoami

For information on which of your identities are in session use
  globus session show

Logout of the Globus CLI with
  globus logout
"""

_LOGIN_EPILOG = (
    (
        u"""\

You have successfully logged in to the Globus CLI!
"""
    )
    + _SHARED_EPILOG
)


@command(
    "consent",
    short_help="Log into Globus to consent to specific Auth or Transfer scopes",
    disable_options=["format", "map_http_status"],
)
@no_local_server_option
@click.argument("scopes", nargs=-1, required=True)
def consent_command(scopes, no_local_server):
    """
    Log into Globus to consent to specific Auth or Transfer scopes

    Does not revoke any existing consents from globus login
    """
    # use a link login if remote session or user requested
    if no_local_server or is_remote_session():
        do_link_auth_flow(scopes=scopes)

    # otherwise default to a local server login flow
    else:
        click.echo(
            "You are running 'globus consent', which should automatically open "
            "a browser window for you to login.\n"
            "If this fails or you experience difficulty, try "
            "'globus consent --no-local-server'"
            "\n---"
        )
        do_local_server_auth_flow(scopes=scopes)

    # print epilog
    click.echo(_LOGIN_EPILOG)
