from uuid import UUID

import click

from globus_sdk.exc import TransferAPIError
from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.services.transfer.helpers import get_client


@click.command('locate', help='Output <UUID>:<path> of a bookmark; useful in '
                              'a subshell as input to another command')
@common_options
@click.argument('bookmark_id_or_name', required=True)
def bookmark_locate(bookmark_id_or_name):
    """
    Executor for `globus transfer bookmark locate`
    """

    client = get_client()

    # leading/trailing whitespace doesn't make sense for UUIDs and the Transfer
    # service outright forbids it for bookmark names, so we can strip it off
    bookmark_id_or_name = bookmark_id_or_name.strip()

    try:
        UUID(bookmark_id_or_name)  # raises ValueError if argument not a UUID
        res = client.get_bookmark(bookmark_id_or_name.lower())

    except (ValueError, TransferAPIError) as ex:
        if isinstance(ex, TransferAPIError) and ex.code != 'BookmarkNotFound':
            raise

        # either the user provided a string that isn't a UUID (ValueError) or
        # the provided UUID doesn't identity a bookmark (TransferAPIError with
        # code='BookmarkNotFound'); fallback to matching a bookmark by name

        try:
            # n.b. case matters to the Transfer service for bookmark names, so
            # two bookmarks can exist whose names vary only by their case
            res = next(bookmark_row for bookmark_row in client.bookmark_list()
                       if bookmark_row['name'] == bookmark_id_or_name)

        except StopIteration:
            safeprint('No bookmark found for "{}"'.format(bookmark_id_or_name),
                      write_to_stderr=True)
            click.get_current_context().exit(1)

    print('{}:{}'.format(res['endpoint_id'], res['path']))
