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
    return ",".join(sorted({m["role"] for m in res["my_memberships"]}))


def format_session_enforcement(res):
    if res.get("enforce_session"):
        return "strict"
    else:
        return "not strict"


def parse_visibility(res):
    return res["policies"]["group_visibility"]


def group_create_and_update_params(
    f: Optional[Callable] = None, *, create: bool = False
) -> Callable:
    """
    Collection of options consumed by group create and update.
    Passing create as True makes any values required for create
    arguments instead of options.
    """
    if f is None:
        return functools.partial(group_create_and_update_params, create=create)

    # name is required for create
    if create:
        f = click.argument("name")(f)
    else:
        f = click.option("--name", help="Name for the group.")(f)

    f = click.option("--description", help="Description for the group.")(f)

    return f
