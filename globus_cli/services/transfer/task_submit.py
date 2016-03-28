from __future__ import print_function
import json

from globus_sdk import TransferClient
from globus_cli.helpers import outformat_is_json, cliargs, CLIArg
from globus_cli.services.transfer.activation import autoactivate


def add_submission_id(client, datadoc):
    submission_id = client.get_submission_id().data['value']
    datadoc['submission_id'] = submission_id


def _validate_transfer_args(args, parser):
    if (args.source_path is None or args.dest_path is None) and (
            args.batch is None):
        parser.error('async-transfer requires either --source-path and '
                     '--dest-path OR --batch')
    if ((args.source_path is not None and args.batch is not None) or
            (args.dest_path is not None and args.batch is not None)):
        parser.error('async-transfer cannot take --batch in addition to '
                     '--source-path or --dest-path')


@cliargs(('Copy a file or directory from one endpoint '
          'to another as an asynchronous task'), [
    CLIArg('source-endpoint', required=True,
           help='ID of the endpoint from which to transfer'),
    CLIArg('dest-endpoint', required=True,
           help='ID of the endpoint to which to transfer'),
    CLIArg('source-path',
           help='Path to the file/dir to move on source-endpoint'),
    CLIArg('dest-path',
           help='Desired location of the file/dir on dest-endpoint'),
    CLIArg('batch', type=json.loads,
           help=('Paths to source and destination files, as a JSON '
                 'document. Document format is '
                 '{"DATA": [{"source": <path>, "dest": <path>}, ...]}'))
    ], arg_validator=_validate_transfer_args)
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
        transferdata = [_transfer_item(args.source_path, args.dest_path)]

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
          'as an asynchronous task'), [
    CLIArg('endpoint-id', required=True,
           help='ID of the endpoint from which to delete file(s)'),
    CLIArg('path', required=True, help='Path to the file/dir to delete'),
    CLIArg('recursive', default=False, action='store_true',
           help='Recursively delete dirs'),
    CLIArg('ignore-missing', default=False, action='store_true',
           help='Don\'t throw errors if the file or dir is absent')
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
