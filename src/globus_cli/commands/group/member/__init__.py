from globus_cli.parsing import group

from .add import member_add
from .list import member_list
from .remove import member_remove


@group("member")
def group_member() -> None:
    """Manage members in a Globus Group"""


group_member.add_command(member_add)
group_member.add_command(member_remove)
group_member.add_command(member_list)
