import click

from globus_cli.parsing import common_options, task_id_option
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer.helpers import get_client


@click.command('show', help='Show detailed information about a specific Task')
@common_options
@task_id_option(helptext='ID of the Task which you want to examine')
def show_task(task_id):
    """
    Executor for `globus transfer task show`
    """
    client = get_client()

    res = client.get_task(task_id)

    print_json_response(res)
