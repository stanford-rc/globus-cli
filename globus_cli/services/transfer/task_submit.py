from __future__ import print_function
import json
import argparse

from globus_sdk import TransferClient
from globus_cli.helpers import outformat_is_json, cliargs
from globus_cli.services.transfer.activation import autoactivate


def add_submission_id(client, datadoc):
    submission_id = client.get_submission_id().data['value']
    datadoc['submission_id'] = submission_id


def _validate_transfer_args(args, parser):
    if (args.source is None or args.dest is None) and args.batch is None:
        parser.error('async-transfer requires either --source-path and '
                     '--dest-path OR --batch')
    if ((args.source is not None and args.batch is not None) or
            (args.dest is not None and args.batch is not None)):
        parser.error('async-transfer cannot take --batch in addition to '
                     '--source-path or --dest-path')


@cliargs(('Copy a file or directory from one endpoint '
          'to another as an asynchronous task'),
         [(['--source-endpoint'],
           {'dest': 'source_endpoint', 'required': True,
            'help': 'ID of the endpoint from which to transfer'}),
          (['--dest-endpoint'],
           {'dest': 'dest_endpoint', 'required': True,
            'help': 'ID of the endpoint to which to transfer'}),
          (['--source-path'],
           {'dest': 'source',
            'help': 'Path to the file/dir to move on source-endpoint'}),
          (['--dest-path'],
           {'dest': 'dest',
            'help': 'Desired location of the file/dir on dest-endpoint'}),
          (['--batch'],
           {'dest': 'batch', 'type': json.loads,
            'help': ('Paths to source and destination files, as a JSON '
                     'document. Document format is '
                     '{"DATA": [{"source": <path>, "dest": <path>}, ...]}')})
          ],
         arg_validator=_validate_transfer_args)
def submit_transfer(args):
    """
    Executor for `globus transfer async-transfer`
    """
    def _transfer_item(src, dst):
        return {
            'DATA_TYPE': 'transfer_item',
            'source_path': src,
            'destination_path': dst
        }

    if args.batch is not None:
        transferdata = []
        for item in args.batch['DATA']:
            transferdata.append(_transfer_item(item['source'], item['dest']))
    else:
        transferdata = [_transfer_item(args.source, args.dest)]

    datadoc = {
        'DATA_TYPE': 'transfer',
        'label': 'globus-cli transfer',
        'source_endpoint': args.source_endpoint,
        'destination_endpoint': args.dest_endpoint,
        'sync_level': 2,
        'DATA': transferdata
    }

    client = TransferClient()
    autoactivate(client, args.source_endpoint, if_expires_in=60)
    autoactivate(client, args.dest_endpoint, if_expires_in=60)

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
    autoactivate(client, args.endpoint_id, if_expires_in=60)

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
