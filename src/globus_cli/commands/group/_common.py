import functools
from typing import Callable, Optional

import click


def group_id_arg(f: Optional[Callable] = None, *, required=True):
    """
    By default, the group ID is made required; pass `required=False` to the
    decorator arguments to make it optional.
    """
    if f is None:
        return functools.partial(group_id_arg, required=required)
    return click.argument("GROUP_ID", required=required)(f)


def parse_roles(res):
    roles = set()
    for membership in res["my_memberships"]:
        roles.add(membership["role"])

    return ",".join(sorted(roles))


def format_session_enforcement(res):
    if res.get("enforce_session"):
        return "strict"
    else:
        return "not strict"


def parse_visibility(res):
    return res["policies"]["group_visibility"]


def group_create_and_update_params(f: Optional[Callable] = None) -> Callable:
    """
    Collection of options consumed by group create and update.
    """
    if f is None:
        return functools.partial(group_create_and_update_params)

    f = click.argument("name")(f)
    f = click.option("--description", help="Description for the group.")(f)

    return f
