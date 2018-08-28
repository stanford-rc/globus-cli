from globus_cli.parsing import globus_group

from globus_cli.commands.session.boost import session_boost
from globus_cli.commands.session.show import session_show


@globus_group(name="session", help="Manage your CLI auth session")
def session_command():
    pass


# commands
session_command.add_command(session_boost)
session_command.add_command(session_show)
