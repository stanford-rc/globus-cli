from __future__ import print_function
import json

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json, cliargs
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format, endpoint_list_to_text)
from globus_cli.services.transfer.activation import autoactivate


@cliargs('Search for Globus Endpoints',
         [(['--filter-scope'],
           {'dest': 'scope', 'default': None,
            'choices': ('all', 'my-endpoints', 'my-gcp-endpoints',
                        'recently-used', 'in-use', 'shared-by-me',
                        'shared-with-me'),
            'help': ('The set of endpoints to search over. '
                     'Omission is equivalent to "all"')}),
          (['--filter-fulltext'],
           {'dest': 'fulltext', 'default': None,
            'help': 'Text filter to apply to the selected set of endpoints.'})
          ])
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


@cliargs('Activate an Endpoint via autoactivation',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')})
          ])
def endpoint_autoactivate(args):
    """
    Executor for `globus transfer endpoint-autoactivate`
    """
    client = TransferClient()
    res = autoactivate(client, args.endpoint_id)
    print(json.dumps(res.data, indent=2))


@cliargs('Deactivate an Endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')})
          ])
def endpoint_deactivate(args):
    """
    Executor for `globus transfer endpoint-deactivate`
    """
    client = TransferClient()
    res = client.endpoint_deactivate(args.endpoint_id)
    print(json.dumps(res.data, indent=2))


@cliargs('List all servers belonging to an Endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')})
          ])
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
            print(text_col_format.format(result.data['uri']))


@cliargs('List all Shared Endpoints on an Endpoint by the current user',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')})
          ])
def my_shared_endpoint_list(args):
    """
    Executor for `globus transfer endpoint my-shared-endpoint-list`
    """
    client = TransferClient()

    ep_iterator = client.my_shared_endpoint_list(args.endpoint_id)

    if outformat_is_json(args):
        print_json_from_iterator(ep_iterator)
    else:
        endpoint_list_to_text(ep_iterator)


@cliargs('List of assigned Roles on an Endpoint',
         [(['--endpoint-id'],
           {'dest': 'endpoint_id', 'required': True,
            'help': ('ID of the endpoint, typically fetched '
                     'from endpoint-search')})
          ])
def endpoint_role_list(args):
    """
    Executor for `globus transfer access endpoint-role-list`
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
                result.data['principal_type'], result.data['principal'],
                result.data['role']))
