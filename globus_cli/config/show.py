from __future__ import print_function
import click

from globus_cli.helpers import common_options
from globus_cli.config.helpers import load_config


@click.command('show', help='Show a value from the Globus Config')
@common_options
@click.argument('parameter', required=True)
def show_command(parameter):
    """
    Executor for `globus config show`
    """
    conf = load_config()

    section = 'general'
    if '.' in parameter:
        section, parameter= parameter.split('.', 1)

    try:
        value = conf[section][parameter]
    except KeyError:
        print('{} not set'.format(parameter))
    else:
        print('{} = {}'.format(parameter, value))
