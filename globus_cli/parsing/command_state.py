import click

from globus_cli import config
from globus_cli.parsing.case_insensitive_choice import CaseInsensitiveChoice


# Format Enum for output formatting
# could use a namedtuple, but that's overkill
JSON_FORMAT = 'json'
TEXT_FORMAT = 'text'


class CommandState(object):
    def __init__(self):
        # default is config value, or TEXT if it's not set
        self.output_format = config.get_output_format() or TEXT_FORMAT

    def outformat_is_text(self):
        return self.output_format == TEXT_FORMAT

    def outformat_is_json(self):
        return self.output_format == JSON_FORMAT


def format_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(CommandState)
        # need to do an OR check here because this is invoked with value=None
        # everywhere that the `-F`/`--format` option is omitted (each level of
        # the command tree)
        state.output_format = (value or state.output_format).lower()
        return state.output_format

    return click.option(
        '-F', '--format',
        type=CaseInsensitiveChoice([JSON_FORMAT, TEXT_FORMAT]),
        help='Output format for stdout. Defaults to text',
        expose_value=False, callback=callback)(f)
