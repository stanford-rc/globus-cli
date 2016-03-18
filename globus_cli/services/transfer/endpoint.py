from __future__ import print_function

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format, endpoint_list_to_text)


def endpoint_search(args):
    """
    Executor for `globus transfer endpoint-search`
    """
    client = TransferClient()
    search_iterator = client.endpoint_search(
        filter_fulltext=args.fulltext, filter_scope=args.scope)

    if outformat_is_json(args):
        print_json_from_iterator(search_iterator)
    else:
        endpoint_list_to_text(search_iterator)


def endpoint_autoactivate(args):
    """
    Executor for `globus transfer endpoint-autoactivate`
    """
    client = TransferClient()
    res = client.endpoint_autoactivate(args.endpoint_id)
    print(res.text_body)


def endpoint_server_list(args):
    """
    Executor for `globus transfer endpoint-server-list`
    """
    client = TransferClient()

    server_iterator = client.endpoint_server_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(server_iterator)
    else:
        text_col_format = text_header_and_format(
            [(36, 'URI')])

        for result in server_iterator:
            print(text_col_format.format(result['uri']))


def my_shared_endpoint_list(args):
    """
    Executor for `globus transfer endpoint-my-shared-endpoint-list`
    """
    client = TransferClient()

    ep_iterator = client.my_shared_endpoint_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(ep_iterator)
    else:
        endpoint_list_to_text(ep_iterator)


def endpoint_role_list(args):
    """
    Executor for `globus transfer endpoint-role-list`
    """
    client = TransferClient()

    role_iterator = client.endpoint_role_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(role_iterator)
    else:
        text_col_format = text_header_and_format(
            [(16, 'Principal Type'), (36, 'Principal'), (16, 'Role')])

        for result in role_iterator:
            print(text_col_format.format(
                result['principal_type'], result['principal'], result['role']))
