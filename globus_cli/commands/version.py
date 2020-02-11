from globus_cli.helpers import print_version
from globus_cli.parsing import command


@command("version", disable_options=["format", "map_http_status"])
def version_command():
    """Show the version and exit"""
    print_version()
