from globus_cli.parsing import globus_main_func

from globus_cli.commands.list_commands import list_commands
from globus_cli.commands.config_command import config_command

from globus_cli.commands.login import login_command
from globus_cli.commands.whoami import whoami_command

from globus_cli.commands.get_identities import get_identities_command
from globus_cli.commands.ls import ls_command

from globus_cli.services.transfer import transfer_command


@globus_main_func
def main():
    pass


main.add_command(list_commands)
main.add_command(config_command)

main.add_command(login_command)
main.add_command(whoami_command)

main.add_command(get_identities_command)
main.add_command(ls_command)

main.add_command(transfer_command)
