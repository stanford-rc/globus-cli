import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, EndpointPlusPath
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate

path_type = EndpointPlusPath()


@click.command('mkdir', help='Make a directory on an Endpoint')
@common_options
@click.argument('endpoint_plus_path', required=True,
                metavar=path_type.metavar, type=path_type)
def mkdir_command(endpoint_plus_path):
    """
    Executor for `globus transfer mkdir`
    """
    endpoint_id, path = endpoint_plus_path

    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    res = client.operation_mkdir(endpoint_id, path=path)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
