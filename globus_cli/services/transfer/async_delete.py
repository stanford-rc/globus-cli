from __future__ import print_function
import click

from globus_sdk import DeleteData


from globus_cli.helpers import (
    common_options, outformat_is_json, print_json_response)
from globus_cli.services.transfer.helpers import (
    get_client, endpoint_id_option, shlex_process_stdin, submission_id_option)
from globus_cli.services.transfer.activation import autoactivate


@click.command('async-delete', short_help='Submit a Delete Task',
               help=('Delete a file or directory from one Endpoint as an '
                     'asynchronous task.'))
@common_options
@submission_id_option
@endpoint_id_option(help='ID of the Endpoint from which to delete file(s)')
@click.option('--path', help='Path to the file/dir to delete')
@click.option('--recursive', is_flag=True, help='Recursively delete dirs')
@click.option('--ignore-missing', is_flag=True,
              help="Don't throw errors if the file or dir is absent")
@click.option('--batch', is_flag=True,
              help=('Accept a batch of paths on stdin (i.e. run in '
                    'batchmode). Uses --endpoint-id as passed on the '
                    'commandline.'))
def async_delete_command(batch, ignore_missing, recursive, path, endpoint_id,
                         submission_id):
    """
    Executor for `globus transfer async-delete`
    """
    if path is None and (not batch):
        raise click.UsageError(
            'async-delete requires either --path OR --batch')
    if path is not None and batch:
        raise click.UsageError(
            'async-delete cannot take --batch in addition to --path')

    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    delete_data = DeleteData(client, endpoint_id,
                             label='globus-cli delete',
                             recursive=recursive,
                             ignore_missing=ignore_missing)

    if batch is not None:
        # although this sophisticated structure (like that in async-transfer)
        # isn't strictly necessary, it gives us the ability to add options in
        # the future to these lines with trivial modifications
        @click.command()
        @click.argument('path')
        def process_batch_line(path):
            """
            Parse a line of batch input and add it to the delete submission
            item.
            """
            delete_data.add_item(path)

        shlex_process_stdin(
            process_batch_line, 'Enter paths to delete, line by line.')

    else:
        delete_data.add_item(path)

    if submission_id is not None:
        delete_data['submission_id'] = submission_id

    res = client.submit_delete(delete_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
