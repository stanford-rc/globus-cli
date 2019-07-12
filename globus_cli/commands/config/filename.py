import click

from globus_cli.config import get_config_obj
from globus_cli.parsing import common_options


@click.command("filename", help="Output the path of the config file")
@common_options(no_format_option=True, no_map_http_status_option=True)
def filename_command():
    """
    Executor for `globus config filename`
    """
    try:
        config = get_config_obj(file_error=True)
    except IOError as e:
        click.echo(e, err=True)
        click.get_current_context().exit(1)
    else:
        click.echo(config.filename)
