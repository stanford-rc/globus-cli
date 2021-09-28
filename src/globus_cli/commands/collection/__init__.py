from globus_cli.parsing import group

from .delete import collection_delete
from .show import collection_show
from .update import collection_update


@group("collection")
def collection_command() -> None:
    """Manage your Collections"""


# commands
collection_command.add_command(collection_delete)
collection_command.add_command(collection_show)
collection_command.add_command(collection_update)
