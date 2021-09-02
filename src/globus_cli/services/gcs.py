from typing import Dict, cast

import click
from globus_sdk import GCSClient, RefreshTokenAuthorizer

from globus_cli import version
from globus_cli.login_manager import internal_auth_client, token_storage_adapter

from .transfer import EndpointType
from .transfer import get_client as get_transfer_client


def get_gcs_client(gcs_id: str, *, require_auth=True) -> GCSClient:
    adapter = token_storage_adapter()
    tokens = adapter.get_token_data(gcs_id)
    authorizer = None

    # if there are tokens, build the authorizer
    if tokens is not None:
        authorizer = RefreshTokenAuthorizer(
            tokens["refresh_token"],
            internal_auth_client(),
            access_token=tokens["access_token"],
            expires_at=tokens["expires_at_seconds"],
            on_refresh=adapter.on_refresh,
        )
    elif require_auth:
        raise ValueError(
            f"Could not get login data for GCS {gcs_id}. "
            f"Try login with '--gcs {gcs_id}' to fix."
        )

    tc = get_transfer_client()
    gcs_address = tc.get_endpoint(gcs_id)["DATA"][0]["hostname"]

    return GCSClient(gcs_address, authorizer=authorizer, app_name=version.app_name)


def get_collection_endpoint_id(
    collection_id: str, command_remap: Dict[EndpointType, str]
) -> str:
    tc = get_transfer_client()
    endpoint_record = tc.get_endpoint(collection_id)
    ep_type = EndpointType.determine_endpoint_type(endpoint_record)
    if ep_type not in (
        EndpointType.MAPPED_COLLECTION,
        EndpointType.GUEST_COLLECTION,
    ):
        nice_type_name = EndpointType.nice_name(ep_type)
        err_msg_common = (
            f"Expected {collection_id} to be a collection ID.\n"
            f"Instead, found it was of type '{nice_type_name}'.\n\n"
        )
        if ep_type not in command_remap:
            raise click.ClickException(
                err_msg_common
                + "This operation is not supported on objects of this type."
            )
        else:
            raise click.ClickException(
                err_msg_common + "Please run the following command instead:\n\n"
                f"    {command_remap[ep_type]} {collection_id}\n"
            )

    return cast(str, endpoint_record["owner_id"])
