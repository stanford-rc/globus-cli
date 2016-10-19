import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, ENDPOINT_PLUS_REQPATH
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer.helpers import get_client


@click.command('create', help='Create a Bookmark for the current user')
@common_options
@click.option('--name', required=True,
              help='Name for the Bookmark')
@click.argument('endpoint_plus_path', metavar=ENDPOINT_PLUS_REQPATH.metavar,
                type=ENDPOINT_PLUS_REQPATH)
def bookmark_create(name, endpoint_plus_path):
    """
    Executor for `globus transfer bookmark create`
    """
    endpoint_id, path = endpoint_plus_path
    client = get_client()

    submit_data = {
        'endpoint_id': endpoint_id,
        'path': path,
        'name': name
    }

    res = client.create_bookmark(submit_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint('Bookmark ID: {}'.format(res['id']))
