"""
Setup a custom except hook which formats exceptions that are uncaught.
In "DEBUGMODE", we'll just use the typical sys.excepthook behavior and print a
stacktrace. It's really for debugging problems with the CLI itself, but it
might also come in handy if we have issues with the way that we're trying to
format an exception.
Define an except hook per exception type that we want to treat specially,
generally types of SDK errors, and dispatch onto tht set of hooks.
"""
import sys
import os

import click

from globus_sdk import exc
from globus_cli.safeio import safeprint, write_error_info, PrintableErrorField


def pagination_overrun_hook():
    write_error_info(
        'Internal Paging Error',
        [PrintableErrorField(
            'details', ('Some kind of paging error happened. '
                        'Likely an issue with the CLI or Globus SDK.'))])


def transferapi_hook(exception):
    write_error_info(
        'Transfer API Error',
        [PrintableErrorField('HTTP status', exception.http_status),
         PrintableErrorField('request_id', exception.request_id),
         PrintableErrorField('code', exception.code),
         PrintableErrorField('message', exception.message, multiline=True)])


def globusapi_hook(exception):
    write_error_info(
        'GLobus API Error',
        [PrintableErrorField('HTTP status', exception.http_status),
         PrintableErrorField('code', exception.code),
         PrintableErrorField('message', exception.message, multiline=True)])


def custom_except_hook(exc_info):
    """
    A custom excepthook to present python errors produced by the CLI.
    We don't want to show end users big scary stacktraces if they aren't python
    programmers, so slim it down to some basic info. We keep a "DEBUGMODE" env
    variable kicking around to let us turn on stacktraces if we ever need them.

    Additionally, does global suppression of EPIPE errors, which often occur
    when a python command is piped to a consumer like `head` which closes its
    input stream before python has sent all of its output.
    DANGER: There is a (small) risk that this will bite us if there are EPIPE
    errors produced within the Globus SDK. We should keep an eye on this
    possibility, as it may demand more sophisticated handling of EPIPE.
    Possible TODO item to reduce this risk: inspect the exception and only hide
    EPIPE if it comes from within the globus_cli package.
    """
    exception_type, exception, traceback = exc_info

    # check if we're in debug mode, and run the real excepthook if we are
    if os.environ.get('GLOBUS_CLI_DEBUGMODE', None) is not None:
        sys.excepthook(exception_type, exception, traceback)

    # we're not in debug mode, do custom handling
    else:
        # if it's a click exception, re-raise as original -- Click's main
        # execution context will handle pretty-printing
        if isinstance(exception, click.ClickException):
            raise exception_type, exception, traceback

        # handle the Globus-raised errors with our special hooks
        # these will present the output (on stderr) as JSON
        elif exception_type is exc.PaginationOverrunError:
            pagination_overrun_hook()
        elif exception_type is exc.TransferAPIError:
            transferapi_hook(exception)
        elif exception_type is exc.GlobusAPIError:
            globusapi_hook(exception)
        else:
            safeprint('{}: {}'.format(exception_type.__name__, exception))
