import click
from globus_sdk import LocalGlobusConnectPersonal

from globus_cli.parsing import common_options, one_use_option


@click.command("local-id", help="Display UUID of locally installed endpoint")
@common_options(no_format_option=True, no_map_http_status_option=True)
@one_use_option(
    "--personal",
    is_flag=True,
    default=True,
    help="Use local Globus Connect Personal endpoint (default) ",
)
def local_id(personal):
    """
    Executor for `globus endpoint local-id`
    """
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
