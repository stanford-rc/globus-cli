"""
Logic for using client identities with the Globus CLI
"""
import os

import globus_sdk

CLIENT_ID = os.getenv("GLOBUS_CLI_CLIENT_ID")
CLIENT_SECRET = os.getenv("GLOBUS_CLI_CLIENT_SECRET")


def is_client_login() -> bool:
    """
    Return True if the correct env variables have been set to use a
    client identity with the Globus CLI
    """
    if CLIENT_ID is None and CLIENT_SECRET is None:
        return False

    elif isinstance(CLIENT_ID, str) and isinstance(CLIENT_SECRET, str):
        return True

    else:
        raise ValueError(
            "Both GLOBUS_CLI_CLIENT_ID and GLOBUS_CLI_CLIENT_SECRET must "
            "be set to use a client identity. Either set both environment "
            "variables, or unset them to use a normal login."
        )


def get_client_login() -> globus_sdk.ConfidentialAppAuthClient:
    """
    Return the ConfidentialAppAuthClient for the client identity
    logged into the CLI
    """
    if CLIENT_ID is None or CLIENT_SECRET is None:
        raise ValueError("No client identity is logged in")

    return globus_sdk.ConfidentialAppAuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
