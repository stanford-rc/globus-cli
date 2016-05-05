from __future__ import print_function
import click

from globus_cli.helpers import (
    common_options, print_json_response, outformat_is_json)
from globus_cli.services.transfer.helpers import (
    get_client, endpoint_id_option, assemble_generic_doc)
from globus_cli.services.transfer.endpoint.server.helpers import (
    add_and_update_opts)


@click.command('add', help='Add a server to an Endpoint')
@common_options
@add_and_update_opts(add=True)
@endpoint_id_option
def server_add(endpoint_id, subject, port, scheme, hostname):
    """
    Executor for `globus transfer endpoint server add`
    """
    client = get_client()

    server_doc = assemble_generic_doc(
        'server',
        subject=subject, port=port, scheme=scheme, hostname=hostname)

    res = client.add_endpoint_server(endpoint_id, server_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
        print('ID: {}'.format(res['id']))
