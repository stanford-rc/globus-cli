from __future__ import print_function
import json

from globus_sdk import TransferClient
from globus_cli.helpers import outformat_is_json


def submit_transfer(args):
    """
    Executor for `globus transfer submit-transfer`
    """
    client = TransferClient()
    submission_id = client.get_submission_id().data['value']

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
    res = client.submit_transfer(submission_id, datadoc)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print(res.data['message'])


def submit_delete(args):
    """
    Executor for `globus transfer submit-delete`
    """
    client = TransferClient()
    submission_id = client.get_submission_id().data['value']

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
    res = client.submit_delete(submission_id, datadoc)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print(res.data['message'])
