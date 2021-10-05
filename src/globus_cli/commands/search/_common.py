from typing import Callable

import click


def index_id_arg(f: Callable) -> Callable:
    return click.argument("index_id", metavar="INDEX_ID", type=click.UUID)(f)
