from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.safeio import formatted_print
from globus_cli.services.transfer import ENDPOINT_LIST_FIELDS, get_client


@command("my-shared-endpoint-list")
@endpoint_id_arg
def my_shared_endpoint_list(endpoint_id):
    """List all shared endpoints on an endpoint by the current user"""
    client = get_client()
    ep_iterator = client.my_shared_endpoint_list(endpoint_id)

    formatted_print(ep_iterator, fields=ENDPOINT_LIST_FIELDS)
