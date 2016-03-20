from __future__ import print_function

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format)


def bookmark_list(args):
    """
    Executor for `globus transfer bookmark-list`
    """
    client = TransferClient()

    bookmark_iterator = client.bookmark_list()

    if outformat_is_json(args):
        print_json_from_iterator(bookmark_iterator)
    else:
        text_col_format = text_header_and_format(
            [(32, 'Name'), (36, 'Endpoint ID'), (None, 'Path')])

        for result in bookmark_iterator:
            print(text_col_format.format(
                result.data['name'], result.data['endpoint_id'],
                result.data['path']))
