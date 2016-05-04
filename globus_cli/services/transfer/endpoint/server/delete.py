from __future__ import print_function
import click

from globus_cli.helpers import common_options, print_json_response
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('delete', help='Delete a server belonging to an Endpoint')
@common_options
@click.option('--server-id', required=True,
              help='ID of the server on ENDPOINT_ID')
@endpoint_id_option
def server_delete(endpoint_id, server_id):
    """
    Executor for `globus transfer endpoint server show`
    """
    client = get_client()

    server_doc = client.delete_endpoint_server(endpoint_id, server_id)

    print_json_response(server_doc)
