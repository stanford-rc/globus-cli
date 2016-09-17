import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_option
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate


@click.command('rename', help='Rename a file or directory on an Endpoint')
@common_options
@endpoint_id_option
@click.option('--old-path', required=True,
              help='Path to the file/dir to rename')
@click.option('--new-path', required=True,
              help='Desired location of the file/dir after rename')
def rename_command(new_path, old_path, endpoint_id):
    """
    Executor for `globus transfer rename`
    """
    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    res = client.operation_rename(endpoint_id, oldpath=old_path,
                                  newpath=new_path)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
