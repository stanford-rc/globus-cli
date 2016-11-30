import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import print_table, outformat_is_json
from globus_cli.services.transfer import get_client, print_json_from_iterator


@click.command('list', help='List all servers belonging to an Endpoint')
@common_options
@endpoint_id_arg
def server_list(endpoint_id):
    """
    Executor for `globus endpoint server list`
    """
    client = get_client()

    endpoint = client.get_endpoint(endpoint_id)

    if endpoint['host_endpoint_id']:  # not GCS -- this is a share endpoint
        raise click.UsageError(
            "{id} ({display_name}) is a share and does not have servers.\n"
            "\n"
            "To see details of the share, use\n"
            "    globus endpoint show {id}\n"
            "\n"
            "To list the servers on the share's host endpoint, use\n"
            "    globus endpoint server list {host_endpoint_id}".
            format(**endpoint.data)
        )

    server_iterator = client.endpoint_server_list(endpoint_id)

    if outformat_is_json():
        print_json_from_iterator(server_iterator)
    else:
        print_table(server_iterator, [('ID', 'id'), ('URI', 'uri')])
