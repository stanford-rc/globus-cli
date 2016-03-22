from __future__ import print_function
import json

from globus_sdk import TransferClient
from globus_cli.helpers import outformat_is_json, cliargs


def add_submission_id(client, datadoc):
    submission_id = client.get_submission_id().data['value']
    datadoc['submission_id'] = submission_id


@cliargs(('Copy a file or directory from one endpoint '
          'to another as an asynchronous task'),
         [(['--source-endpoint'],
           {'dest': 'source_endpoint', 'required': True,
            'help': 'ID of the endpoint from which to transfer'}),
          (['--dest-endpoint'],
           {'dest': 'dest_endpoint', 'required': True,
            'help': 'ID of the endpoint to which to transfer'}),
          (['--source-path'],
           {'dest': 'source', 'required': True,
            'help': 'Path to the file/dir to move on source-endpoint'}),
          (['--dest-path'],
           {'dest': 'dest', 'required': True,
            'help': 'Desired location of the file/dir on dest-endpoint'})
          ])
def submit_transfer(args):
    """
    Executor for `globus transfer submit-transfer`
    """
    client = TransferClient()

    datadoc = {
        'DATA_TYPE': 'transfer',
        'label': 'globus-cli transfer',
        'source_endpoint': args.source_endpoint,
        'destination_endpoint': args.dest_endpoint,
        'sync_level': 2,
        'DATA': [
            {
                'DATA_TYPE': 'transfer_item',
                'source_path': args.source,
                'destination_path': args.dest
            }
        ]
    }
    add_submission_id(client, datadoc)
    res = client.submit_transfer(datadoc)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print(res.data['message'])


@cliargs(('Delete a file or directory from one endpoint '
          'as an asynchronous task'),
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': 'ID of the endpoint from which to delete file(s)'}),
          (['--path'],
           {'dest': 'path', 'required': True,
            'help': 'Path to the file/dir to delete'}),
          (['--recursive'],
           {'dest': 'recursive', 'default': False,
            'help': 'Recursively delete dirs', 'action': 'store_true'}),
          (['--ignore-missing'],
           {'dest': 'ignore_missing', 'default': False,
            'help': 'Don\'t throw errors if the file or dir is absent',
            'action': 'store_true'})
          ])
def submit_delete(args):
    """
    Executor for `globus transfer submit-delete`
    """
    client = TransferClient()

    datadoc = {
        'DATA_TYPE': 'delete',
        'label': 'globus-cli delete',
        'endpoint': args.endpoint_id,
        'recursive': args.recursive,
        'ignore_missing': args.ignore_missing,
        'DATA': [
            {
                'DATA_TYPE': 'delete_item',
                'path': args.path
            }
        ]
    }
    add_submission_id(client, datadoc)
    res = client.submit_delete(datadoc)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print(res.data['message'])
