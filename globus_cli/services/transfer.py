from __future__ import print_function

import json

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json, outformat_is_text


def display_name_or_cname(ep_doc):
    return ep_doc['display_name'] or ep_doc['canonical_name']


def endpoint_search(args):
    """
    Executor for `globus transfer endpoint-search`
    """
    client = TransferClient()

    params = {}

    text_col_format = '{:<32} | {:<36} | {}'
    if outformat_is_text(args):
        print(text_col_format.format('Owner', 'ID', 'Display Name'))
        print(text_col_format.format('-'*32, '-'*36, '-'*len('Display Name')))

    for result in client.endpoint_search(
            args.fulltext, filter_scope=args.scope, **params):
        if outformat_is_json(args):
            print(json.dumps(result))
        else:
            print(text_col_format.format(
                result['owner_string'], result['id'],
                display_name_or_cname(result)))


def endpoint_autoactivate(args):
    """
    Executor for `globus transfer endpoint-autoactivate`
    """
    client = TransferClient()
    res = client.endpoint_autoactivate(args.endpoint_id)
    print(res.text_body)


def op_ls(args):
    """
    Executor for `globus transfer ls`
    """
    client = TransferClient()
    res = client.operation_ls(args.endpoint_id, path=args.path)
    print(res.text_body)
