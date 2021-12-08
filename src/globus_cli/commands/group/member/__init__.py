from globus_cli.commands.group.member.add import member_add
from globus_cli.parsing import group


@group("member")
def group_member() -> None:
    """Manage members in a Globus Group"""


group_member.add_command(member_add)
