from __future__ import print_function

import sys

from globus_cli.parser.shared_parser import GlobusCLISharedParser
from globus_cli.parser.command_tree import build_command_tree


def _gen_parser():
    """
    Produces a top-level argument parser built out of all of the various
    subparsers for different services.
    """
    # create the top parser and give it subparsers
    top_level_parser = GlobusCLISharedParser()
    subparsers = top_level_parser.add_subparsers(
        title='Commands',
        parser_class=GlobusCLISharedParser, metavar='')

    build_command_tree(subparsers)

    # return the created parser in all of its glory
    return top_level_parser


def _load_args():
    """
    Load commandline arguments, and do any necessary post-processing.
    """
    parser = _gen_parser()
    args = parser.parse_args()

    return args


def run_command():
    """
    Whatever arguments were loaded, they set a function to be invoked on the
    arguments themselves -- somewhat circular, but a nifty way of passing the
    args to a function that this module doesn't even know about
    """
    args = _load_args()
    try:
        args.func(args)
    except NotImplementedError as e:
        print('NotImplementedError: {}'.format(e.message), file=sys.stderr)
        sys.exit(1)
