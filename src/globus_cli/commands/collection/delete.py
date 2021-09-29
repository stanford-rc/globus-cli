from globus_cli.endpointish import Endpointish
from globus_cli.login_manager import LoginManager
from globus_cli.parsing import collection_id_arg, command
from globus_cli.services.gcs import get_gcs_client
from globus_cli.termio import FORMAT_TEXT_RAW, formatted_print


@command("delete", short_help="Delete an existing Collection")
@collection_id_arg
@LoginManager.requires_login(LoginManager.TRANSFER_RS, pass_manager=True)
def collection_delete(login_manager, *, collection_id):
    """
    Delete an existing Collection. This requires the administrator role on the
    Endpoint.
    """
    epish = Endpointish(collection_id)
    endpoint_id = epish.get_collection_endpoint_id()
    login_manager.assert_logins(endpoint_id, assume_gcs=True)

    client = get_gcs_client(endpoint_id, gcs_address=epish.get_gcs_address())
    res = client.delete_collection(collection_id)
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="code")
