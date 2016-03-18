from __future__ import print_function

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format)


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
                result['principal_type'], result['principal'],
                result['permissions'], result['path']))
