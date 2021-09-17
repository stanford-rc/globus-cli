import functools

import click
import globus_sdk

from globus_cli.parsing.command_state import CommandState

_REGISTERED_HOOKS = []


def error_handler(*, error_class=None, condition=None):
    """decorator for excepthooks

    register each one, in order, with any relevant "condition"
    """

    def inner_decorator(fn):
        @functools.wraps(fn)
        def wrapped(exception):
            fn(exception)
            ctx = click.get_current_context()
            if isinstance(exception, globus_sdk.GlobusAPIError):
                # get the mapping by looking up the state and getting the mapping attr
                mapping = ctx.ensure_object(CommandState).http_status_map

                # if there is a mapped exit code, exit with that. Otherwise, exit 1
                if exception.http_status in mapping:
                    ctx.exit(mapping[exception.http_status])
            ctx.exit(1)

        _REGISTERED_HOOKS.append((wrapped, error_class, condition))
        return wrapped

    return inner_decorator


def find_handler(exception):
    for handler, error_class, condition in _REGISTERED_HOOKS:
        if error_class is not None and not isinstance(exception, error_class):
            continue
        if condition is not None and not condition(exception):
            continue
        return handler
    return None
