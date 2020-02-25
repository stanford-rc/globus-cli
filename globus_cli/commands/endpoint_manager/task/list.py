import click

from globus_cli.parsing import command
from globus_cli.safeio import formatted_print
from globus_cli.services.transfer import get_client, iterable_response_to_dict


def _format_date_range_callback(ctx, param, value):
    if value == (None, None):
        return None
    start, end = value
    formatted = (
        start.strftime("%Y-%m-%d %H:%M:%S") + "," + end.strftime("%Y-%m-%d %H:%M:%S")
    )
    if start > end:
        raise click.UsageError("Bad date range, start after end: {}".format(formatted))
    return formatted


def _comma_join_callback(ctx, param, value):
    if value is None:
        return None
    return ",".join(value)


@command("list")
@click.option("--limit", default=10, show_default=True, help="Limit number of results")
@click.option(
    "--filter-task-id",
    multiple=True,
    type=click.UUID,
    callback=_comma_join_callback,
    help=(
        "Task ID by which to filter. "
        "This option can be used multiple times, "
        "but cannot be combined with other filters"
    ),
)
@click.option(
    "--filter-endpoint-id",
    type=click.UUID,
    help="Filter to tasks with this Endpoint as the Source or Destination",
)
@click.option(
    "--filter-status",
    "-s",
    multiple=True,
    type=click.Choice(["ACTIVE", "INACTIVE", "FAILED", "SUCCEEDED"]),
    default=["ACTIVE"],
    show_default=True,
    callback=_comma_join_callback,
    help="Task status to filter results by. This option can be used multiple times",
)
@click.option(
    "--filter-completion-time",
    type=click.DateTime(),
    nargs=2,
    default=(None, None),
    callback=_format_date_range_callback,
    help=(
        "Filter results to tasks that were completed in a given time range. "
        "Requires two date strings as arguments"
    ),
)
def list_command(
    limit, filter_task_id, filter_status, filter_completion_time, filter_endpoint_id
):
    """
    List Tasks visible to the current user via Endpoint Roles

    Tasks may be visible via Endpoint Manager, Activity Monitor, or similar roles on
    Endpoints. This command lists tasks which can be seen via those role capabilities,
    not the user's own tasks.

    To list your own tasks, use 'globus task list' instead.

    For any query that doesn’t specify a --filter-status that is a subset of
        ("ACTIVE", "INACTIVE")
    at least one of --filter-task-id or --filter-endpoint is required.
    """

    client = get_client()
    task_iterator = client.endpoint_manager_task_list(
        num_results=limit,
        filter_status=filter_status,
        filter_task_id=filter_task_id,
        filter_endpoint=filter_endpoint_id,
    )

    fields = [
        ("Task ID", "task_id"),
        ("Status", "status"),
        ("Type", "type"),
        ("Source Display Name", "source_endpoint_display_name"),
        ("Dest Display Name", "destination_endpoint_display_name"),
        ("Label", "label"),
    ]
    formatted_print(
        task_iterator, fields=fields, json_converter=iterable_response_to_dict
    )
