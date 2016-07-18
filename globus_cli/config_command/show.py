from __future__ import print_function
import click

from globus_cli.helpers import common_options
from globus_cli.config import lookup_option


@click.command('show', help='Show a value from the Globus Config')
@common_options(no_format_option=True)
@click.argument('parameter', required=True)
def show_command(parameter):
    """
    Executor for `globus config show`
    """
    section = 'general'
    if '.' in parameter:
        section, parameter = parameter.split('.', 1)

    value = lookup_option(parameter, section=section)

    if value is None:
        print('{} not set'.format(parameter))
    else:
        print('{} = {}'.format(parameter, value))
