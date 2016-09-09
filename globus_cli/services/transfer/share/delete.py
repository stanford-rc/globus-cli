import click

from globus_cli.safeio import safeprint
from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import get_client, endpoint_id_option


@click.command('delete', help='Delete a given Share')
@common_options
@endpoint_id_option(help='ID of the Share')
def share_delete(endpoint_id):
    """
    Executor for `globus transfer share delete`
    """
    client = get_client()

    res = client.delete_endpoint(endpoint_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
