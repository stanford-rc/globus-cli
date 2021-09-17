from globus_sdk import GroupsClient, RefreshTokenAuthorizer

from globus_cli import version
from globus_cli.login_manager import internal_auth_client, token_storage_adapter


def get_groups_client() -> GroupsClient:
    adapter = token_storage_adapter()
    tokens = adapter.get_token_data("groups.api.globus.org")

    authorizer = RefreshTokenAuthorizer(
        tokens["refresh_token"],
        internal_auth_client(),
        access_token=tokens["access_token"],
        expires_at=tokens["expires_at_seconds"],
        on_refresh=adapter.on_refresh,
    )

    return GroupsClient(authorizer=authorizer, app_name=version.app_name)
