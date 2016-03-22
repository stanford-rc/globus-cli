from __future__ import print_function
import sys


# Format Enum for output formatting
# could use a namedtuple, but that's overkill
JSON_FORMAT = 'json'
TEXT_FORMAT = 'text'


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


def cliargs(helptext, arguments):
    """
    Decorator that takes a function and adds CLI arguments and helptext to it
    as function attributes. The function can then be placed directly into the
    command hierarchy of the _COMMAND_TREE and will be unpacked and inspected
    by parser building.
    """
    def inner_decorator(wrapped):
        """
        The decorator produced by invoking cliargs() on some arguments.
        Doesn't need to create a closure over the wrapped function or anything:
        just takes the arguments to cliargs() and puts them into attributes of
        the function.
        """
        wrapped.cli_help = helptext
        wrapped.cli_arguments = arguments

        return wrapped

    return inner_decorator
