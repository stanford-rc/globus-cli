import webbrowser

import click

from globus_cli.config import (
    AUTH_AT_EXPIRES_OPTNAME,
    AUTH_AT_OPTNAME,
    AUTH_RT_OPTNAME,
    TRANSFER_AT_EXPIRES_OPTNAME,
    TRANSFER_AT_OPTNAME,
    TRANSFER_RT_OPTNAME,
    internal_auth_client,
    lookup_option,
    write_option,
)
from globus_cli.helpers.local_server import LocalServerError, start_local_server

DEFAULT_SCOPES = (
    "openid profile email "
    "urn:globus:auth:scope:auth.globus.org:view_identity_set "
    "urn:globus:auth:scope:transfer.api.globus.org:all"
)


def do_link_auth_flow(
        session_params=None, force_new_client=False, scopes=DEFAULT_SCOPES):
    """
    Prompts the user with a link to authenticate with globus auth
    and authorize the CLI to act on their behalf.
    """
    session_params = session_params or {}

    # get the ConfidentialApp client object
    auth_client = internal_auth_client(
        requires_instance=True, force_new_client=force_new_client
    )

    # start the Confidential App Grant flow
    auth_client.oauth2_start_flow(
        redirect_uri=auth_client.base_url + "v2/web/auth-code",
        refresh_tokens=True,
        requested_scopes=scopes,
    )

    # prompt
    additional_params = {"prompt": "login"}
    additional_params.update(session_params)
    linkprompt = "Please authenticate with Globus here"
    click.echo(
        "{0}:\n{1}\n{2}\n{1}\n".format(
            linkprompt,
            "-" * len(linkprompt),
            auth_client.oauth2_get_authorize_url(additional_params=additional_params),
        )
    )

    # come back with auth code
    auth_code = click.prompt("Enter the resulting Authorization Code here").strip()

    # finish auth flow
    exchange_code_and_store_config(auth_client, auth_code)
    return True


def do_local_server_auth_flow(
        session_params=None, force_new_client=False, scopes=DEFAULT_SCOPES):
    """
    Starts a local http server, opens a browser to have the user authenticate,
    and gets the code redirected to the server (no copy and pasting required)
    """
    session_params = session_params or {}

    # start local server and create matching redirect_uri
    with start_local_server(listen=("127.0.0.1", 0)) as server:
        _, port = server.socket.getsockname()
        redirect_uri = "http://localhost:{}".format(port)

        # get the ConfidentialApp client object and start a flow
        auth_client = internal_auth_client(
            requires_instance=True, force_new_client=force_new_client
        )
        auth_client.oauth2_start_flow(
            refresh_tokens=True, redirect_uri=redirect_uri, requested_scopes=scopes
        )
        additional_params = {"prompt": "login"}
        additional_params.update(session_params)
        url = auth_client.oauth2_get_authorize_url(additional_params=additional_params)

        # open web-browser for user to log in, get auth code
        webbrowser.open(url, new=1)
        auth_code = server.wait_for_code()

    if isinstance(auth_code, LocalServerError):
        click.echo("Authorization failed: {}".format(auth_code), err=True)
        click.get_current_context().exit(1)
    elif isinstance(auth_code, Exception):
        click.echo(
            "Authorization failed with unexpected error:\n{}".format(auth_code),
            err=True,
        )
        click.get_current_context().exit(1)

    # finish auth flow and return true
    exchange_code_and_store_config(auth_client, auth_code)
    return True


def exchange_code_and_store_config(auth_client, auth_code):
    """
    Finishes auth flow after code is gotten from command line or local server.
    Exchanges code for tokens and gets user info from auth.
    Stores tokens and user info in config.
    """
    # do a token exchange with the given code
    tkn = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    tkn = tkn.by_resource_server

    # extract access tokens from final response
    transfer_tkns = tkn.get("transfer.api.globus.org")
    if transfer_tkns:
        transfer_at = transfer_tkns["access_token"]
        transfer_at_expires = transfer_tkns["expires_at_seconds"]
        transfer_rt = transfer_tkns["refresh_token"]

        # revoke any existing tokens
        for token_opt in (
            TRANSFER_RT_OPTNAME,
            TRANSFER_AT_OPTNAME,
        ):
            token = lookup_option(token_opt)
            if token:
                auth_client.oauth2_revoke_token(token)

        # write new tokens to config
        write_option(TRANSFER_RT_OPTNAME, transfer_rt)
        write_option(TRANSFER_AT_OPTNAME, transfer_at)
        write_option(TRANSFER_AT_EXPIRES_OPTNAME, transfer_at_expires)

    auth_tkns = tkn.get("auth.globus.org")
    if auth_tkns:
        auth_at = auth_tkns["access_token"]
        auth_at_expires = auth_tkns["expires_at_seconds"]
        auth_rt = auth_tkns["refresh_token"]

        # revoke any existing tokens
        for token_opt in (
            AUTH_RT_OPTNAME,
            AUTH_AT_OPTNAME,
        ):
            token = lookup_option(token_opt)
            if token:
                auth_client.oauth2_revoke_token(token)

        # write new tokens to config
        write_option(AUTH_RT_OPTNAME, auth_rt)
        write_option(AUTH_AT_OPTNAME, auth_at)
        write_option(AUTH_AT_EXPIRES_OPTNAME, auth_at_expires)
