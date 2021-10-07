from globus_cli.commands.group.list import group_list
from globus_cli.parsing import group


@group("group")
def group_command() -> None:
    """Manage Globus Groups"""


group_command.add_command(group_list)
