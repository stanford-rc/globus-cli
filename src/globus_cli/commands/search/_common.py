from typing import Callable

import click

from globus_cli.types import FIELD_LIST_T


def index_id_arg(f: Callable) -> Callable:
    return click.argument("index_id", metavar="INDEX_ID", type=click.UUID)(f)


def task_id_arg(f: Callable) -> Callable:
    return click.argument("task_id", metavar="TASK_ID", type=click.UUID)(f)


INDEX_FIELDS: FIELD_LIST_T = [
    ("Index ID", "id"),
    ("Display Name", "display_name"),
    ("Status", "status"),
]
