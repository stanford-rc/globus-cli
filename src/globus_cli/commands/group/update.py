from typing import Any

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command
from globus_cli.termio import formatted_print

from ._common import group_create_and_update_params, group_id_arg


@group_create_and_update_params()
@group_id_arg
@command("update", short_help="Update an existing group")
@LoginManager.requires_login(LoginManager.GROUPS_RS)
def group_update(group_id, *, login_manager: LoginManager, **kwargs: Any):
    """Update an existing group. Any fields not given will be set to null."""
    groups_client = login_manager.get_groups_client()

    # response = groups_client.update_group(group_id, kwargs)
    response = groups_client.put(f"/groups/{group_id}", data=kwargs)

    formatted_print(response, simple_text="Group updated successfully")
