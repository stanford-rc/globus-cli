#!/usr/bin/env python

from __future__ import print_function

import sys


def stderr_prompt(prompt):
    """
    Prompt for input on stderr.
    Good for not muddying redirected output while prompting the user.
    """
    print(prompt, file=sys.stderr, end='')
    return raw_input('')


def is_interactive():
    """
    Is the command being run interactively, is output in a pipeline?
    """
    return sys.stdout.isatty()


def input_is_interactive():
    """
    Is the input on stdin coming from a shell, or part of a pipeline?
    """
    return sys.stdin.isatty()


def err_is_interactive():
    """
    Is the stderr going to a shell, or being redirected somewhere else?
    """
    return sys.stderr.isatty()


def require_interactive_input(message='Non-interactive input is not allowed.'):
    """
    Require that the shell input is interactive.
    Fail and exit if the condition is not met.
    """
    if not input_is_interactive():
        print(message, file=sys.stderr)
        sys.exit(1)


def require_interactive_err(message='Non-interactive stderr is not allowed.'):
    """
    Require that the shell error output is interactive.
    Fail and exit if the condition is not met.
    """
    if not err_is_interactive():
        # still print to stderr -- it's what we meant
        print(message, file=sys.stderr)
        sys.exit(1)
