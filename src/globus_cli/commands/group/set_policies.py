import click

from typing import Any

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command
from globus_cli.termio import formatted_print

from ._common import group_id_arg


@click.option(
    "--high-assurance/--not-high-assurance",
    help="Flag if the group will enforce high assurance access policies or not."
)
@click.option(
    "--authentication-timeout",
    type=int,
    help=("Time in seconds before a user must reauthenticate to access a "
          "high assurance group")
)
@click.option(
    "--visibility",
    type=click.Choice(("authenticated", "private"), case_sensitive=False),
    help=(
        "Determine who can see the group. "
        "If authenticated, all authenticated users can see the group. "
        "If private, only members and managers can see the group."
    ),
)
@click.option(
    "--member-visibility",
    type=click.Choice(("members", "managers"), case_sensitive=False),
    help=(
        "Determine who can see members of the group. "
        "If members, members can see all other members. "
        "If managers, only managers can see members."
    ),
)
@click.option(
    "--join-requests/--no-join-requests",
    help="Flag if request to join the group are allowed or not."
)
@click.option(
    "--signup-field",
    type=click.Choice(
        ("institution", "current_project_name", "address", "city", "state",
         "country", "address1", "address2", "zip", "phone", "department",
         "field_of_science"), case_sensitive=False),
    multiple=True,
    help=(
        "Field required from users to apply for group membership. "
        "Pass this option multiple times to require multiple fields. "
        "Any existing required fields will be overwritten if given."
    )
)
@group_id_arg
@command("set-policies")
@LoginManager.requires_login(LoginManager.GROUPS_RS)
def group_set_policies(*, login_manager: LoginManager, group_id: str, **kwargs: Any):
    """Update an existing group's policies"""
    groups_client = login_manager.get_groups_client()

    # get the current state of the group's policies
    existing_policies = groups_client.get_group_policies(group_id)

    # map of groups API field names to CLI option names
    field_option_map = {
        "is_high_assurance": "high_assurance",
        "authentication_assurance_timeout": "authentication_timeout",
        "group_visibility": "visibility",
        "group_members_visibility": "member_visibility",
        "join_requests": "join_requests",
        "signup_fields": "signup_field",
    }

    # assemble data using existing values for any field not given
    print(kwargs)
    data = {}
    for field, existing_value in existing_policies.data.items():
        option_name = field_option_map.get(field)
        if option_name and kwargs.get(option_name) not in (None, ()):
            data[field] = kwargs[option_name]
        else:
            data[field] = existing_value

    response = groups_client.set_group_policies(group_id, data)
    formatted_print(response, simple_text="Group policies updated successfully")
