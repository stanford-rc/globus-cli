from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.safeio import FORMAT_TEXT_RAW, formatted_print
from globus_cli.services.transfer import get_client


@command("deactivate")
@endpoint_id_arg
def endpoint_deactivate(endpoint_id):
    """Deactivate an endpoint"""
    client = get_client()
    res = client.endpoint_deactivate(endpoint_id)
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="message")
