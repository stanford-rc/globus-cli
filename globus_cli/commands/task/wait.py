from globus_cli.parsing import command, synchronous_task_wait_options, task_id_arg
from globus_cli.services.transfer import task_wait_with_io


@command("wait")
@task_id_arg
@synchronous_task_wait_options
def task_wait(meow, heartbeat, polling_interval, timeout, task_id, timeout_exit_code):
    """Wait for a task to complete"""
    task_wait_with_io(
        meow, heartbeat, polling_interval, timeout, task_id, timeout_exit_code
    )
