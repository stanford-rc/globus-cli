from __future__ import print_function
import textwrap
import click

from globus_cli.config import OUTPUT_FORMAT_OPTNAME
from globus_cli.helpers import common_options
from globus_cli.helpers.param_types import CaseInsensitiveChoice
from globus_cli.config_command.helpers import load_config


@click.command('init', help='Initialize your Globus Config file')
@common_options(no_format_option=True)
@click.option('--transfer-token', help='Your Token for Globus Transfer')
@click.option('--auth-token', help='Your Token for Globus Auth')
@click.option('--default-output-format',
              help='The default format for the CLI to use when printing.',
              type=CaseInsensitiveChoice(['json', 'text']))
def init_command(default_output_format, auth_token, transfer_token):
    """
    Executor for `globus config init`
    """
    conf = load_config()

    # check for auth and transfer tokens, prompt if not given
    if not auth_token:
        auth_token = raw_input('\nPlease enter your Globus Auth Token '
                               '(general.auth_token): ')
    if not transfer_token:
        transfer_token = raw_input('\nPlease enter your Globus Transfer Token '
                                   '(general.transfer_token): ')

    # set these any time that `globus config init` is run
    conf['general']['auth_token'] = auth_token
    conf['general']['transfer_token'] = transfer_token

    # now handle the output format, requires a little bit more care
    # first, prompt if it isn't given, but be clear that we have a sensible
    # default if they don't set it
    # then, make sure that if it is given, it's a valid format (discard
    # otherwise)
    # finally, set it only if given and valid
    if not default_output_format:
        print('\n' + textwrap.fill(
            'This must be one of "json" or "text". Other values will be '
            'ignored. ENTER to skip.'))
        default_output_format = raw_input(
            'Default CLI output format (cli.{}) [text]: '
            .format(OUTPUT_FORMAT_OPTNAME)).lower()
        if default_output_format not in ('json', 'text'):
            default_output_format = None

    if default_output_format:
        if 'cli' not in conf:
            conf['cli'] = {}
        conf['cli'][OUTPUT_FORMAT_OPTNAME] = default_output_format

    # write to disk
    print('\n\nWriting updated config to {}'.format(conf.filename))
    conf.write()
