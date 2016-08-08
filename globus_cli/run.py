from __future__ import print_function
import click

from globus_cli.parsing import globus_main_func

from globus_cli.list_commands import list_commands
from globus_cli.config_command import config_command
from globus_cli.helpers import common_options

from globus_cli.services.auth import auth_command
from globus_cli.services.transfer import transfer_command


@click.command('login', short_help='Show Login Help for the CLI',
               help=('Get authentication credentials for the Globus CLI. '
                     'Necessary before any Globus CLI commands which require '
                     'authentication will work'))
@common_options
def login_help():
    print('\nTo login to the Globus CLI, go to\n')
    print('    https://tokens.globus.org/\n')
    print('and select the the "Globus CLI" option.\n')


@globus_main_func
@common_options
def main():
    pass


main.add_command(auth_command)
main.add_command(transfer_command)
main.add_command(login_help)
main.add_command(list_commands)
main.add_command(config_command)
