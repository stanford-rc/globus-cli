import os
from typing import Any, Dict, Iterator, List, Optional, Tuple

import click
import globus_sdk.tokenstorage

from globus_cli.login_manager import token_storage_adapter
from globus_cli.parsing import command
from globus_cli.termio import FORMAT_TEXT_TABLE, formatted_print
from globus_cli.types import FIELD_LIST_T


# TODO: upstream this into the SDK as a method of the SQLiteStorageAdapter
def _iter_namespaces(adapter: globus_sdk.tokenstorage.SQLiteAdapter) -> Iterator[str]:
    conn = adapter._connection

    cursor = conn.execute("SELECT DISTINCT namespace FROM token_storage;")
    for row in cursor:
        yield row[0]


def _profilestr_to_datadict(s: str) -> Optional[Dict[str, Any]]:
    if s.count("/") < 1:
        return None
    if s.count("/") < 2:
        category, env = s.split("/")
        if category == "clientprofile":  # should not be possible
            return None
        return {"client": False, "env": env, "profile": None, "default": True}
    else:
        category, env, profile = s.split("/", 2)
        return {
            "client": category == "clientprofile",
            "env": env,
            "profile": profile,
            "default": False,
        }


def _parse_and_filter_profiles(
    all: bool,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    namespaces = list(_iter_namespaces(token_storage_adapter()))
    globus_env = os.getenv("GLOBUS_SDK_ENVIRONMENT", "production")

    client_profiles = []
    user_profiles = []
    for n in namespaces:
        data = _profilestr_to_datadict(n)
        if not data:  # skip any parse failures
            continue
        if (
            data["env"] != globus_env and not all
        ):  # unless --all was passed, skip other envs
            continue
        if data["client"]:
            client_profiles.append(data)
        else:
            if all or data["profile"] is not None:
                user_profiles.append(data)

    return (client_profiles, user_profiles)


@command(
    "cli-profile-list",
    disable_options=["format", "map_http_status"],
)
@click.option("--all", is_flag=True, hidden=True)
def cli_profile_list(*, all: bool) -> None:
    """
    List all CLI profiles which have been used

    These are the values for GLOBUS_PROFILE which have been recorded, as well as
    GLOBUS_CLI_CLIENT_ID values which have been used.
    """

    client_profiles, user_profiles = _parse_and_filter_profiles(all)

    if user_profiles:
        fields: FIELD_LIST_T = [("GLOBUS_PROFILE", "profile")]
        if all:
            fields += [
                ("GLOBUS_SDK_ENVIRONMENT", "env"),
                ("is_default", lambda x: "True" if x["default"] else "False"),
            ]
        formatted_print(user_profiles, text_format=FORMAT_TEXT_TABLE, fields=fields)
    if client_profiles:
        click.echo(
            """
==========
"""
        )
        fields = [("GLOBUS_CLI_CLIENT_ID", "profile")]
        if all:
            fields.append(("GLOBUS_SDK_ENVIRONMENT", "env"))
        formatted_print(client_profiles, text_format=FORMAT_TEXT_TABLE, fields=fields)
