import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer import autoactivate, get_client


@click.command('autoactivate', help='Activate an Endpoint via autoactivation')
@common_options
@endpoint_id_arg
def endpoint_autoactivate(endpoint_id):
    """
    Executor for `globus endpoint autoactivate`
    """
    client = get_client()
    res = autoactivate(client, endpoint_id)
    print_json_response(res)
