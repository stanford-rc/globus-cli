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

    formatted_print(
        groups,
        fields=[
            ("Group ID", "id"),
            ("Name", "name"),
            ("Type", "group_type"),
            ("High Assurance", "enforce_session"),
        ],
    )
