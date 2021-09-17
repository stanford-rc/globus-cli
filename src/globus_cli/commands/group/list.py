from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command
from globus_cli.services.groups import get_groups_client
from globus_cli.termio import formatted_print


@command("list", short_help="List groups you belong to")
@LoginManager.requires_login(LoginManager.GROUPS_RS)
def group_list():
    """List all groups for the current user"""
    client = get_groups_client()

    groups = client.get_my_groups()

    def _format_session_enforcement(res):
        if res.get("enforce_session"):
            return "strict"
        else:
            return "not strict"

    def _parse_roles(res):
        roles = set()
        for membership in res["my_memberships"]:
            roles.add(membership["role"])

        return ",".join(sorted(roles))

    formatted_print(
        groups,
        fields=[
            ("Group ID", "id"),
            ("Name", "name"),
            ("Type", "group_type"),
            ("Session Enforcement", _format_session_enforcement),
            ("Roles", _parse_roles),
        ],
    )
