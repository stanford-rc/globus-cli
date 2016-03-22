from __future__ import print_function

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json, cliargs
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format)


@cliargs('List of Access Control List rules on an Endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')})
          ])
def endpoint_acl_list(args):
    """
    Executor for `globus transfer endpoint-acl-list`
    """
    client = TransferClient()

    rule_iterator = client.endpoint_acl_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(rule_iterator)
    else:
        text_col_format = text_header_and_format(
            [(16, 'Principal Type'), (36, 'Principal'), (None, 'Permissions'),
             (None, 'Path')])

        for result in rule_iterator:
            print(text_col_format.format(
                result.data['principal_type'], result.data['principal'],
                result.data['permissions'], result.data['path']))
