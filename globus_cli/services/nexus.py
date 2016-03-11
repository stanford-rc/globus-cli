from __future__ import print_function

import getpass
import json

from globus_cli.helpers import stderr_prompt

from globus_sdk import NexusClient


def get_goauth_token(args):
    """
    Executor for `globus nexus get-goauth-token`
    Reads username and password from stdin if they aren't in the args.
    """
    # get username and/or password if not present
    if not args.username:
        args.username = stderr_prompt('GlobusID Username: ')
    if not args.password:
        args.password = getpass.getpass('GlobusID Password: ')

    # get the token itself
    client = NexusClient()
    tok = client.get_goauth_token(args.username, args.password)

    # print it out in JSON or TEXT format, then exit
    if args.outformat == 'json':
        print(json.dumps({'token': tok}))
    else:
        print(tok)
