from __future__ import print_function
import click

from globus_cli.helpers.param_types import CaseInsensitiveChoice
from globus_cli.version import __version__


# Format Enum for output formatting
# could use a namedtuple, but that's overkill
JSON_FORMAT = 'json'
TEXT_FORMAT = 'text'


def outformat_is_json():
    """
    Only safe to call within a click context.
    """
    ctx = click.get_current_context()
    return ctx.obj['format'] == JSON_FORMAT


def outformat_is_text():
    """
    Only safe to call within a click context.
    """
    ctx = click.get_current_context()
    return ctx.obj['format'] == TEXT_FORMAT


def endpoint_id_option(*args, **kwargs):
    def decorate(f, **kwargs):
        """
        Work of actually decorating a function -- wrapped in here because we
        want to dispatch depending on how this is invoked
        """
        help = kwargs.get('help', 'ID of the Endpoint')
        f = click.option('--endpoint-id', required=True, help=help)(f)
        return f

    # special behavior when invoked with only one non-keyword argument: act as
    # a normal decorator, decorating and returning that argument with
    # click.option
    if len(args) == 1 and len(kwargs) == 0:
        return decorate(args[0])

    # if we're not doing that, we should see no positional args
    # the alternative behavior is to fall through and discard *args, but this
    # will probably confuse someone in the future when their arguments are
    # silently discarded
    elif len(args) != 0:
        raise ValueError(
                'endpoint_id_option() cannot take positional args')

    # final case: got 0 or more kwargs, no positionals
    # do the function-which-returns-a-decorator dance to produce a
    # new decorator based on the arguments given
    else:
        def inner_decorator(f):
            return decorate(f, **kwargs)
        return inner_decorator


def common_options(*args, **kwargs):
    def decorate(f, **kwargs):
        """
        Work of actually decorating a function -- wrapped in here because we
        want to dispatch depending on how this is invoked
        """
        f = click.version_option(__version__)(f)
        f = click.help_option('-h', '--help')(f)

        def format_callback(ctx, param, value):
            ctx.obj['format'] = value or ctx.obj.get('format')

            return ctx.obj['format']

        if not kwargs.get('no_format_option'):
            f = click.option(
                '-F', '--format',
                type=CaseInsensitiveChoice([JSON_FORMAT, TEXT_FORMAT]),
                help='Output format for stdout. Defaults to text',
                expose_value=False, callback=format_callback)(f)

        return f

    # special behavior when invoked with only one non-keyword argument: act as
    # a normal decorator, decorating and returning that argument with
    # click.option
    if len(args) == 1 and len(kwargs) == 0:
        return decorate(args[0])

    # if we're not doing that, we should see no positional args
    # the alternative behavior is to fall through and discard *args, but this
    # will probably confuse someone in the future when their arguments are
    # silently discarded
    elif len(args) != 0:
        raise ValueError(
                'common_options() cannot take positional args')

    # final case: got 0 or more kwargs, no positionals
    # do the function-which-returns-a-decorator dance to produce a
    # new decorator based on the arguments given
    else:
        def inner_decorator(f):
            return decorate(f, **kwargs)
        return inner_decorator
