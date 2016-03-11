from globus_sdk import TransferClient


def endpoint_search(args):
    """
    Executor for `globus transfer endpoint-search`
    """
    client = TransferClient()

    params = {}

    if args.scope:
        params['filter_scope'] = args.scope
    if args.fulltext:
        params['filter_fulltext'] = args.fulltext

    res = client.endpoint_search(**params)

    print(res.text_body)


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
