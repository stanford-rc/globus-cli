import errno
import click

from globus_cli.safeio.check_pty import (
    term_is_interactive, err_is_terminal, out_is_terminal)


def safeprint(message, write_to_stderr=False, newline=True):
    """
    Wrapper around click.echo used to encapsulate its functionality.
    Also protects against EPIPE during click.echo calls, as this can happen
    normally in piped commands when the consumer closes before the producer.
    """
    try:
        click.echo(message, nl=newline, err=write_to_stderr)
    except IOError as err:
        if err.errno is errno.EPIPE:
            pass
        else:
            raise


def print_command_hint(message):
    """
    Wrapper around safeprint that checks terminal state
    before printing a given command hint message
    """
    if term_is_interactive() and err_is_terminal() and out_is_terminal():
        safeprint(message, write_to_stderr=True)
