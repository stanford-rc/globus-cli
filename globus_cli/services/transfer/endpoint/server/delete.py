from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, print_json_response, outformat_is_json)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option
from globus_cli.services.transfer.endpoint.server.helpers import (
    server_id_option)


@click.command('delete', help='Delete a server belonging to an Endpoint')
@common_options
@server_id_option
@endpoint_id_option
def server_delete(endpoint_id, server_id):
    """
    Executor for `globus transfer endpoint server show`
    """
    client = get_client()

    server_doc = client.delete_endpoint_server(endpoint_id, server_id)

    if outformat_is_json():
        print_json_response(server_doc)
    else:
        print(server_doc['message'])
