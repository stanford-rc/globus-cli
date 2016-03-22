from __future__ import print_function

from globus_sdk import TransferClient

from globus_cli.helpers import outformat_is_json, cliargs
from globus_cli.services.transfer.helpers import (
    print_json_from_iterator, text_header_and_format)


@cliargs('List Tasks for the current user', [])
def task_list(args):
    """
    Executor for `globus transfer task-list`
    """
    client = TransferClient()

    task_iterator = client.task_list(num_results=10,
                                     filter='type:TRANSFER,DELETE')

    if outformat_is_json(args):
        print_json_from_iterator(task_iterator)
    else:
        text_col_format = text_header_and_format(
            [(36, 'Task ID'), (16, 'Status'), (16, 'Type'),
             (36, 'Source'), (36, 'Dest')])

        for result in task_iterator:
            print(text_col_format.format(
                result.data['task_id'], result.data['status'],
                result.data['type'],
                result.data['source_endpoint_id'],
                result.data['destination_endpoint_id']))


@cliargs('List Events for a given Task',
         [(['--task-id'],
           {'dest': 'task_id', 'required': True,
            'help': 'ID of the task for which you want to list events.'})
          ])
def task_event_list(args):
    """
    Executor for `globus transfer task-event-list`
    """
    client = TransferClient()

    event_iterator = client.task_event_list(args.task_id)

    if outformat_is_json(args):
        print_json_from_iterator(event_iterator)
    else:
        text_col_format = text_header_and_format(
            [(25, 'Time'), (32, 'Code'), (8, 'Is Error'), (None, 'Details')])

        for result in event_iterator:
            print(text_col_format.format(
                result.data['time'], result.data['code'],
                result.data['is_error'], result.data['details']))
