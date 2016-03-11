from globus_sdk import TransferClient


def endpoint_search(args):
    client = TransferClient()

    params = {}

    if args.scope:
        params['filter_scope'] = args.scope
    if args.fulltext:
        params['filter_fulltext'] = args.fulltext

    res = client.endpoint_search(**params)

    print(res.text_body)
