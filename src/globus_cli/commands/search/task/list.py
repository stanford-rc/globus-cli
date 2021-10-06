import uuid

from globus_cli.parsing import command
from globus_cli.services.search import get_search_client
from globus_cli.termio import FORMAT_TEXT_TABLE, formatted_print

from .._common import index_id_arg

TASK_FIELDS = [
    ("State", "state"),
    ("Task ID", "task_id"),
    ("Creation Date", "creation_date"),
    ("Completion Date", "completion_date"),
]


@command("list", short_help="List recent Tasks for an index")
@index_id_arg
def list_command(index_id: uuid.UUID):
    """List the 1000 most recent Tasks for an index"""
    search_client = get_search_client()
    formatted_print(
        search_client.get_task_list(index_id),
        fields=TASK_FIELDS,
        text_format=FORMAT_TEXT_TABLE,
        response_key="tasks",
    )
