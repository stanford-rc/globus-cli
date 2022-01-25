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
    """Update an existing group."""
    groups_client = login_manager.get_groups_client()

    # get the current state of the group
    group = groups_client.get_group(group_id)

    # assemble put data using existing values for any field not given
    data = {}
    for field in ["name", "description"]:
        if kwargs.get(field) is not None:
            data[field] = kwargs.get(field)
        else:
            data[field] = group[field]

    # response = groups_client.update_group(group_id, kwargs)
    response = groups_client.put(f"/groups/{group_id}", data=data)

    formatted_print(response, simple_text="Group updated successfully")
