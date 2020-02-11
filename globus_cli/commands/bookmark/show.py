import click

from globus_cli.commands.bookmark.helpers import resolve_id_or_name
from globus_cli.parsing import command
from globus_cli.safeio import FORMAT_TEXT_RECORD, formatted_print, is_verbose
from globus_cli.services.transfer import get_client


@command("show")
@click.argument("bookmark_id_or_name")
def bookmark_show(bookmark_id_or_name):
    """
    Given a bookmark name or ID resolves bookmark in endpoint:path format.
    Use --verbose for additional fields.
    """
    client = get_client()
    res = resolve_id_or_name(client, bookmark_id_or_name)
    formatted_print(
        res,
        text_format=FORMAT_TEXT_RECORD,
        fields=(
            ("ID", "id"),
            ("Name", "name"),
            ("Endpoint ID", "endpoint_id"),
            ("Path", "path"),
        ),
        simple_text=(
            # standard output is endpoint:path format
            "{}:{}".format(res["endpoint_id"], res["path"])
            # verbose output includes all fields
            if not is_verbose()
            else None
        ),
    )
