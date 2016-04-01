from __future__ import print_function

import json

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json, cliargs, CLIArg
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format)


@cliargs('List Bookmarks for the current user', [])
def bookmark_list(args):
    """
    Executor for `globus transfer bookmark list`
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


@cliargs('Create a Bookmark for the current user', [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint on which to add a Bookmark'),
    CLIArg('path', required=True,
           help='Path on the endpoint for the Bookmark'),
    CLIArg('name', required=True,
           help='Name for the Bookmark')
    ])
def bookmark_create(args):
    """
    Executor for `globus transfer bookmark create`
    """
    client = TransferClient()

    submit_data = {
        'endpoint_id': args.endpoint_id,
        'path': args.path,
        'name': args.name
    }

    res = client.create_bookmark(submit_data)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print('Bookmark ID: {}'.format(res.data['id']))
