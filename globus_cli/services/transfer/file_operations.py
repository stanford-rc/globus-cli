from __future__ import print_function
import json

from globus_sdk import TransferClient
from globus_cli.helpers import outformat_is_json, cliargs
from globus_cli.services.transfer.activation import autoactivate


@cliargs('List the contents of a directory on an endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')}),
          (['--path'],
           {'dest': 'path', 'default': '/',
            'help': ('Path on the remote endpoint to list. '
                     'Defaults to "/"')})
          ])
def op_ls(args):
    """
    Executor for `globus transfer ls`
    """
    client = TransferClient()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    res = client.operation_ls(args.endpoint_id, path=args.path)
    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        for item in res.data['DATA']:
            print(item['name'])


@cliargs('Make a directory on an Endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')}),
          (['--path'],
           {'dest': 'path', 'required': True,
            'help': 'Path on the remote endpoint to create'})
          ])
def op_mkdir(args):
    """
    Executor for `globus transfer mkdir`
    """
    client = TransferClient()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    res = client.operation_mkdir(args.endpoint_id, path=args.path)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print(res.data['message'])


@cliargs('Rename a file or directory on an Endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')}),
          (['--old-path'],
           {'dest': 'oldpath', 'required': True,
            'help': 'Path to the file/dir to rename'}),
          (['--new-path'],
           {'dest': 'newpath', 'required': True,
            'help': 'Desired location of the file/dir after rename'})
          ])
def op_rename(args):
    """
    Executor for `globus transfer rename`
    """
    client = TransferClient()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    res = client.operation_rename(args.endpoint_id, oldpath=args.oldpath,
                                  newpath=args.newpath)

    if outformat_is_json(args):
        print(json.dumps(res.data, indent=2))
    else:
        print(res.data['message'])
