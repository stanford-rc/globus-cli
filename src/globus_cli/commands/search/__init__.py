from globus_cli.parsing import group

from .ingest import ingest_command
from .query import query_command


@group("search")
def search_command():
    """Use Globus Search to store and query for data"""


search_command.add_command(ingest_command)
search_command.add_command(query_command)
