import click

from globus_cli.parsing import common_options
from globus_cli.safeio import formatted_print
from globus_cli.config import (
    CLIENT_ID_OPTNAME, internal_auth_client, lookup_option)


@click.command('close',
               short_help="Close your CLI auth session",
               help=("Close your current CLI auth session."))
@common_options(no_format_option=True, no_map_http_status_option=True)
@click.confirmation_option(
    prompt="Are you sure you want to close your CLI auth session?",
    help='Automatically say "yes" to all prompts')
def session_close():

    client_id = lookup_option(CLIENT_ID_OPTNAME)
    auth_client = internal_auth_client()
    res = auth_client.post(
        "/v2/api/clients/{}/close-session".format(client_id))
    formatted_print(res)
