from __future__ import print_function
import click
import os
import subprocess

from globus_cli.helpers import common_options


@click.command('edit', help='Edit your Globus Config file')
@common_options(no_format_option=True)
def edit_command():
    """
    Executor for `globus config edit`
    """
    editor = os.environ.get('EDITOR', 'nano')
    subprocess.call([editor, os.path.expanduser('~/.globus.cfg')])
