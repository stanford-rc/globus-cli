from __future__ import print_function
import sys

from globus_cli.parser import JSON_FORMAT, TEXT_FORMAT


def stderr_prompt(prompt):
    """
    Prompt for input on stderr.
    Good for not muddying redirected output while prompting the user.
    """
    print(prompt, file=sys.stderr, end='')
    return raw_input()


def outformat_is_json(args):
    return args.outformat == JSON_FORMAT


def outformat_is_text(args):
    return args.outformat == TEXT_FORMAT
