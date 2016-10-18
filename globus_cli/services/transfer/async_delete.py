import click

from globus_sdk import DeleteData


from globus_cli.parsing import (
    common_options, submission_id_option, EndpointPlusPath)
from globus_cli.helpers import (
    outformat_is_json, print_json_response, colon_formatted_print)

from globus_cli.services.transfer.helpers import (
    get_client, shlex_process_stdin)
from globus_cli.services.transfer.activation import autoactivate

path_type = EndpointPlusPath(path_required=False)


@click.command('async-delete', short_help='Submit a Delete Task',
               help=('Delete a file or directory from one Endpoint as an '
                     'asynchronous task.'))
@common_options
@submission_id_option
@click.option('--recursive', is_flag=True, help='Recursively delete dirs')
@click.option('--label', default=None, help=('Set a label for this task'))
@click.option('--ignore-missing', is_flag=True,
              help="Don't throw errors if the file or dir is absent")
@click.option('--batch', is_flag=True,
              help=('Accept a batch of paths on stdin (i.e. run in '
                    'batchmode). Uses ENDPOINT_ID as passed on the '
                    'commandline, and includes any commandline PATH given'))
@click.argument('endpoint_plus_path', metavar=path_type.metavar,
                type=path_type)
def async_delete_command(batch, ignore_missing, recursive, endpoint_plus_path,
                         label, submission_id):
    """
    Executor for `globus transfer async-delete`
    """
    endpoint_id, path = endpoint_plus_path
    if path is None and (not batch):
        raise click.UsageError(
            'async-delete requires either a PATH OR --batch')

    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    delete_data = DeleteData(client, endpoint_id,
                             label=label,
                             recursive=recursive,
                             ignore_missing=ignore_missing)

    if path:
        delete_data.add_item(path)

    if batch:
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

    if submission_id is not None:
        delete_data['submission_id'] = submission_id

    res = client.submit_delete(delete_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        fields = (('Message', 'message'), ('Task ID', 'task_id'))
        colon_formatted_print(res, fields)
