from __future__ import print_function
import click
import sys

from globus_cli.excepthook import custom_except_hook
from globus_cli.list_commands import list_commands
from globus_cli.config_command import config_command
from globus_cli.helpers import common_options

from globus_cli.services.auth import auth_command
from globus_cli.services.transfer import transfer_command


# there is a single global object for all click contexts, a shared dict
_global_click_obj = {}


class TopLevelGroup(click.Group):
    """
    This is a custom command type which is basically a click.Group, but is
    designed specifically for the top level command.
    It's specialization is that it catches all exceptions from subcommands and
    passes them to a custom error handler.
    """
    def invoke(self, ctx):
        try:
            return super(TopLevelGroup, self).invoke(ctx)
        except Exception:
            custom_except_hook(sys.exc_info())


@click.command('login', short_help='Show Login Help for the CLI',
               help=('Get authentication credentials for the Globus CLI. '
                     'Necessary before any Globus CLI commands which require '
                     'authentication will work'))
@common_options
def login_help():
    print('\nTo login to the Globus CLI, go to\n')
    print('    https://tokens.globus.org/\n')
    print('and select the the "Globus CLI" option.\n')


@click.group('globus', context_settings=dict(obj=_global_click_obj),
             cls=TopLevelGroup)
@common_options
def main():
    pass


main.add_command(auth_command)
main.add_command(transfer_command)
main.add_command(login_help)
main.add_command(list_commands)
main.add_command(config_command)
