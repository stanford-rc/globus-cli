from globus_cli.parsing import command, endpoint_id_arg, role_id_arg
from globus_cli.safeio import FORMAT_TEXT_RAW, formatted_print
from globus_cli.services.transfer import get_client


@command("delete")
@endpoint_id_arg
@role_id_arg
def role_delete(role_id, endpoint_id):
    """Remove a role from an endpoint"""
    client = get_client()
    res = client.delete_endpoint_role(endpoint_id, role_id)
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="message")
