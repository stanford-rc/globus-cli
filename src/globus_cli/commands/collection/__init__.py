from globus_cli.parsing import group

from .delete import collection_delete


@group("collection")
def collection_command():
    """Manage your Collections"""


# commands
collection_command.add_command(collection_delete)
