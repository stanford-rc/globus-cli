from globus_cli.parser import GlobusCLISharedParser

from globus_sdk import TransferClient


def add_subcommand_parsers(subparsers):
    """
    Add Globus Transfer commands
    """
    transfer_parser = subparsers.add_parser(
        'transfer', help=(
            'Interact with Globus Transfer API. '
            'Used to inspect, modify, and interact with Globus Endpoints. '
            'Has capabilities to search Endpoints, manage Sharing Access '
            'via Access Control Lists (ACLs), manage Endpoint roles, and '
            'do actual Transfer tasks between endpoints.'))

    subsubparsers = transfer_parser.add_subparsers(
        title='Commands', parser_class=GlobusCLISharedParser, metavar='')

    # individual endpoint CRUD
    add_get_endpoint_parser(subsubparsers)
    add_update_endpoint_parser(subsubparsers)
    add_create_endpoint_parser(subsubparsers)

    # search, activation, and other endpointish actions
    add_endpoint_search_parser(subsubparsers)
    add_endpoint_autoactivate_parser(subsubparsers)

    # Transfer tasks
    add_ls_parser(subsubparsers)


def add_get_endpoint_parser(subsubparsers):
    """
    Subcommand parser for `globus transfer get-endpoint`
    """


def add_update_endpoint_parser(subsubparsers):
    """
    Subcommand parser for `globus transfer update-endpoint`
    """


def add_create_endpoint_parser(subsubparsers):
    """
    Subcommand parser for `globus transfer create-endpoint`
    """


def add_endpoint_search_parser(subsubparsers):
    """
    Subcommand parser for `globus transfer endpoint-search`
    """
    endpoint_search_parser = subsubparsers.add_parser(
        'endpoint-search', help=(
            'Search for Globus Endpoints')
        )
    endpoint_search_parser.set_defaults(func=endpoint_search)

    endpoint_search_parser.add_argument(
        '--filter-scope', dest='scope', default=None,
        choices=('all', 'my-endpoints', 'my-gcp-endpoints', 'recently-used',
                 'in-use', 'shared-by-me', 'shared-with-me'),
        help=('The set of endpoints to search over. '
              'Omission is equivalent to "all"'))
    endpoint_search_parser.add_argument(
        '--filter-fulltext', dest='fulltext', default=None,
        help='Text filter to apply to ')


def add_endpoint_autoactivate_parser(subsubparsers):
    """
    Subcommand parser for `globus transfer endpoint-autoactivate`
    """


def add_ls_parser(subsubparsers):
    """
    Subcommand parser for `globus transfer ls`
    """


def endpoint_search(args):
    client = TransferClient()

    params = {}

    if args.scope:
        params['filter_scope'] = args.scope
    if args.fulltext:
        params['filter_fulltext'] = args.fulltext

    res = client.endpoint_search(**params)

    print(res.text_body)
