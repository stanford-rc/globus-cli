import click

from globus_cli.commands.bookmark.helpers import resolve_id_or_name
from globus_cli.parsing import command
from globus_cli.safeio import FORMAT_TEXT_RAW, formatted_print
from globus_cli.services.transfer import get_client


@command("delete")
@click.argument("bookmark_id_or_name")
def bookmark_delete(bookmark_id_or_name):
    """Delete a bookmark"""
    client = get_client()
    bookmark_id = resolve_id_or_name(client, bookmark_id_or_name)["id"]

    res = client.delete_bookmark(bookmark_id)
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="message")
