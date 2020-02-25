from globus_cli.commands.endpoint_manager.task import task_command
from globus_cli.parsing import group


@group("endpoint-manager")
def endpoint_manager_command():
    """Advanced endpoint and task management, via Endpoint Manager capabilities"""


endpoint_manager_command.add_command(task_command)
