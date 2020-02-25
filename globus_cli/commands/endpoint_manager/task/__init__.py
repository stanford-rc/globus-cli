from globus_cli.commands.endpoint_manager.task.list import list_command
from globus_cli.parsing import group


@group("task")
def task_command():
    """Endpoint-manager Task management"""


task_command.add_command(list_command)
