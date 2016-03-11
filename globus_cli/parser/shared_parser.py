import argparse
import textwrap
import json

import globus_cli


class GlobusCLISharedParser(argparse.ArgumentParser):
    """
    A base parser type from which all other command parsers inherit. Provides
    shared arguments, top level description, and other common attributes.
    """
    def __init__(self, *args, **kwargs):
        # TODO: Update this description to be more informative, accurate
        description = textwrap.dedent("""Run a globus command.
        The globus command is structured to provide a uniform command line
        interface to all Globus services. For more information and tutorials,
        see docs.globus.org
        """)

        # this is marginally nicer than trying to stuff explicit kwargs
        # inbetween *args and **kwargs in the initializer invocation below
        newkwargs = {
            'prog': 'globus',
            'description': description
        }
        newkwargs.update(kwargs)
        argparse.ArgumentParser.__init__(self, *args, **newkwargs)

        # shared arguments

        # output format -- all commands must support these, although they
        # are free to implement the TEXT format however they see fit
        self.add_argument(
            '-F', '--format', dest='outformat',
            default='json', choices=['json', 'text'], type=str.lower,
            help='Output format for stdout.')

        # version of globus cli -- ignores all other passed arguments and
        # prints the version
        self.add_argument('--version', action='version',
                          version='%(prog)s ' + globus_cli.__version__)
