import click

from globus_cli.parsing import common_options
from globus_cli.helpers import outformat_is_json, print_table

from globus_cli.services.transfer import print_json_from_iterator, get_client


class ISOTimeType(click.ParamType):
    """
    Enforces time inputs to be in either YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    And that each value is a valid int that falls in the correct range
    """

    name = "ISO TIME"

    def convert(self, value, param, ctx):
        try:
            if len(value) not in [10, 19]:
                raise ValueError

            year = int(value[:4])
            if year <= 0:
                self.fail("Invalid year {}".format(year))
            month = int(value[5:7])
            if month not in range(1, 13):
                self.fail("Month {} must be in range 1-12.".format(month))
            day = int(value[8:10])
            if day not in range(1, 32):
                self.fail("Day {} must be in range 1-31.".format(day))

            if len(value) == 19:
                hour = int(value[11:13])
                if hour not in range(24):
                    self.fail("Hour {} must be in range 0-23.".format(hour))
                minute = int(value[14:16])
                if minute not in range(60):
                    self.fail(
                        "Minute {} must be in range 0-59.".format(minute))
                second = int(value[17:19])
                if second not in range(61):
                    self.fail(
                        "Second {} must be in range 0-60.".format(second))

            return value
        except (ValueError, IndexError):
            self.fail(
                "Time must be in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")


@click.command('list', help='List Tasks for the current user')
@common_options
@click.option(
    "--limit", default=10, show_default=True, help="Limit number of results.")
@click.option(
    "--filter-task-id", multiple=True, type=click.UUID,
    help="task UUID to filter by. This option can be used multiple times.")
@click.option(
    "--filter-type", type=click.Choice(["TRANSFER", "DELETE"]),
    help="Filter results to only TRANSFER or DELETE tasks.")
@click.option(
    "--filter-status", multiple=True,
    type=click.Choice(["ACTIVE", "INACTIVE", "FAILED", "SUCCEEDED"]),
    help=("Task status to filter results by. "
          "This option can be used multiple times."))
@click.option(
    "--filter-label", multiple=True,
    help=("Filter results to task whose label matches pattern. "
          "This option can be used multiple times."))
@click.option(
    "--filter-not-label", multiple=True,
    help=("Filter not results whose label matches pattern. "
          "This option can be used multiple times."))
@click.option(
    "--inexact / --exact", default=True,
    help=("Allows / disallows --filter-label and --filter-not-label to use"
          "* as a wild-card character and ignore case"))
@click.option(
    "--filter-requested-after", type=ISOTimeType(),
    help="Filter results to tasks that were requested after given time.")
@click.option(
    "--filter-requested-before", type=ISOTimeType(),
    help="Filter results to tasks that were requested before given time.")
@click.option(
    "--filter-completed-after", type=ISOTimeType(),
    help="Filter results to tasks that were completed after given time.")
@click.option(
    "--filter-completed-before", type=ISOTimeType(),
    help="Filter results to tasks that were completed before given time.")
def task_list(limit, filter_task_id, filter_status, filter_type,
              filter_label, filter_not_label, inexact,
              filter_requested_after, filter_requested_before,
              filter_completed_after, filter_completed_before):
    """
    Executor for `globus task-list`
    """

    # make filter string
    filter_string = ""

    if filter_task_id:
        filter_string += "task_id:"
        for item in filter_task_id:
            filter_string += "{},".format(item)
        filter_string = filter_string[:-1] + "/"  # replace trailing , with /

    if filter_type:
        filter_string += "type:{}/".format(filter_type)
    else:
        filter_string += "type:TRANSFER,DELETE/"

    if filter_status:
        filter_string += "status:"
        for item in filter_status:
            filter_string += "{},".format(item)
        filter_string = filter_string[:-1] + "/"  # replace trailing , with /

    if filter_label or filter_not_label:
        filter_string += "label:"
        for item in filter_label:
            if inexact:
                filter_string += "~{},".format(item)
            else:
                filter_string += "={},".format(item)
        for item in filter_not_label:
            if inexact:
                filter_string += "!~{},".format(item)
            else:
                filter_string += "!{},".format(item)
        filter_string = filter_string[:-1] + "/"  # replace trailing , with /

    if filter_requested_after or filter_requested_before:
        filter_string += "request_time:{},{}/".format(
            (filter_requested_after or ""), (filter_requested_before or ""))

    if filter_completed_after or filter_completed_before:
        filter_string += "completion_time:{},{}/".format(
            (filter_completed_after or ""), (filter_completed_before or ""))

    client = get_client()
    task_iterator = client.task_list(
        num_results=limit,
        filter=filter_string[:-1])  # ignore trailing /

    if outformat_is_json():
        print_json_from_iterator(task_iterator)
    else:
        print_table(task_iterator, [
            ('Task ID', 'task_id'), ('Status', 'status'), ('Type', 'type'),
            ('Source Display Name', 'source_endpoint_display_name'),
            ('Dest Display Name', 'destination_endpoint_display_name'),
            ('Label', 'label')])
