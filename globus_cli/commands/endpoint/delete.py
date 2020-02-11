from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.safeio import FORMAT_TEXT_RAW, formatted_print
from globus_cli.services.transfer import get_client


@command("delete")
@endpoint_id_arg
def endpoint_delete(endpoint_id):
    """Delete a given endpoint"""
    client = get_client()
    res = client.delete_endpoint(endpoint_id)
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="message")
