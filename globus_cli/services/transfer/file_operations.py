from __future__ import print_function

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json


def op_ls(args):
    """
    Executor for `globus transfer ls`
    """
    client = TransferClient()
    res = client.operation_ls(args.endpoint_id, path=args.path)
    if outformat_is_json(args):
        print(res.text_body)
    else:
        for item in res.json_body['DATA']:
            print(item['name'])


def op_mkdir(args):
    """
    Executor for `globus transfer mkdir`
    """
    client = TransferClient()
    res = client.operation_mkdir(args.endpoint_id, path=args.path)

    if outformat_is_json(args):
        print(res.text_body)
    else:
        print(res.json_body['message'])


def op_rename(args):
    """
    Executor for `globus transfer rename`
    """
    client = TransferClient()
    res = client.operation_rename(args.endpoint_id, oldpath=args.oldpath,
                                  newpath=args.newpath)

    if outformat_is_json(args):
        print(res.text_body)
    else:
        print(res.json_body['message'])
