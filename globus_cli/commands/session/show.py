import click
import time

import globus_sdk
from globus_cli.parsing import common_options
from globus_cli.safeio import formatted_print
from globus_cli.services.auth import LazyIdentityMap
from globus_cli.config import (
    internal_auth_client, lookup_option, AUTH_AT_OPTNAME)


@click.command("show",
               short_help="Show your current CLI auth session",
               help="List all identities in your current CLI auth session.")
@common_options()
def session_show():
    # introspect the auth access token to get session info
    auth_client = internal_auth_client()
    access_token = lookup_option(AUTH_AT_OPTNAME)

    # only instance clients can introspect tokens
    if isinstance(auth_client, globus_sdk.ConfidentialAppAuthClient):
        res = auth_client.oauth2_token_introspect(
            access_token, include="session_info")
        session_info = res.get("session_info", {})
        authentications = session_info.get("authentications") or {}

    # empty session if still using Native App Client
    else:
        session_info = {}
        authentications = {}

    # resolve ids to human readable usernames
    resolved_ids = LazyIdentityMap(list(authentications))

    # put the nested dicts in a format table output can work with
    # while also converting vals into human readable formats
    list_data = [
        {"id": key,
         "username": resolved_ids.get(key),
         "auth_time": time.strftime(
            '%Y-%m-%d %H:%M %Z', time.localtime(vals["auth_time"]))
         }
        for key, vals in authentications.items()]

    formatted_print(list_data, json_converter=lambda x: session_info,
                    fields=[("Username", "username"),
                            ("ID", "id"),
                            ("Auth Time", "auth_time")])
