import textwrap
import click

from globus_cli.safeio import safeprint
from globus_cli.helpers import common_options
from globus_cli.helpers.param_types import CaseInsensitiveChoice
from globus_cli.config_command.helpers import load_config


@click.command('init',
               help=('Initialize your Globus Config file with any settings '
                     'you may want for the SDK and CLI'))
@common_options(no_format_option=True)
@click.option('--default-output-format',
              help='The default format for the CLI to use when printing.',
              type=CaseInsensitiveChoice(['json', 'text']))
def init_command(default_output_format):
    """
    Executor for `globus config init`
    """
    conf = load_config()

    # now handle the output format, requires a little bit more care
    # first, prompt if it isn't given, but be clear that we have a sensible
    # default if they don't set it
    # then, make sure that if it is given, it's a valid format (discard
    # otherwise)
    # finally, set it only if given and valid
    if not default_output_format:
        safeprint('\n' + textwrap.fill(
            'This must be one of "json" or "text". Other values will be '
            'ignored. ENTER to skip.'))
        default_output_format = raw_input(
            'Default CLI output format (cli.output_format) [text]: ').lower()
        if default_output_format not in ('json', 'text'):
            default_output_format = None

    if default_output_format:
        if 'cli' not in conf:
            conf['cli'] = {}
        conf['cli']['output_format'] = default_output_format

    # write to disk
    safeprint('\n\nWriting updated config to {}'.format(conf.filename))
    conf.write()
