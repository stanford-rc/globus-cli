import click
from globus_sdk import LocalGlobusConnectPersonal

from globus_cli.parsing import command, one_use_option


@command("local-id", disable_options=["format", "map_http_status"])
@one_use_option(
    "--personal",
    is_flag=True,
    default=True,
    help="Use local Globus Connect Personal endpoint (default)",
)
def local_id(personal):
    """Display UUID of locally installed endpoint"""
    if personal:
        try:
            ep_id = LocalGlobusConnectPersonal().endpoint_id
        except IOError as e:
            click.echo(e, err=True)
            click.get_current_context().exit(1)

        if ep_id is not None:
            click.echo(ep_id)
        else:
            click.echo("No Globus Connect Personal installation found.")
            click.get_current_context().exit(1)
