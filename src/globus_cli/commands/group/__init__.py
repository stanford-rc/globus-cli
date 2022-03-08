from globus_cli.commands.group.create import group_create
from globus_cli.commands.group.delete import group_delete
from globus_cli.commands.group.invite import group_invite
from globus_cli.commands.group.list import group_list
from globus_cli.commands.group.member import group_member
from globus_cli.commands.group.show import group_show
from globus_cli.commands.group.update import group_update
from globus_cli.parsing import group


@group("group")
def group_command() -> None:
    """Manage Globus Groups"""


group_command.add_command(group_list)
group_command.add_command(group_show)
group_command.add_command(group_create)
group_command.add_command(group_update)
group_command.add_command(group_delete)
group_command.add_command(group_member)
group_command.add_command(group_invite)
