from globus_cli.parser import GlobusCLISharedParser

from globus_cli.services import nexus, auth, transfer


def _not_implemented_func(args):
    """
    This is a dummy function used to stub parts of the command tree that
    haven't been implemented yet.
    It has the same signature as a typical command function (i.e. takes args
    and nothing else), but raises a NotImplementedError
    """
    raise NotImplementedError(('Hold yer horses! '
                               'This command has not been implemented yet!'))


_COMMAND_TREE = {
    'nexus': {
        'help': ('Interact with legacy Nexus API. WARNING: Deprecated. '
                 'Only use this if you need access to legacy tokens '
                 'during the development of the globus cli. These methods '
                 'will be replaced in the near future with commands '
                 'which use other services.'),
        'commands': {
            'get-goauth-token': {
                'help': 'Get a Legacy GOAuth Token from Globus Nexus.',
                'func': nexus.get_goauth_token,
                'arguments': [
                    (['-u', '--username'],
                     {'dest': 'username', 'default': None,
                      'help': ('Username for a GlobusID user to use to get '
                               'a token.')}
                     ),
                    (['-p', '--password'],
                     {'dest': 'password', 'default': None,
                      'help': ('Password for a GlobusID user to use to get '
                               'a token.')}
                     )
                ]
            }
        }
    },
    'auth': {
        'help': ('Interact with Globus Auth API. '
                 'Used to inspect tokens, identities, identity sets, '
                 'consent to service terms, revoke and manage consents, '
                 'manage OAuth Clients, and a variety of other '
                 'Authorization and Authentication based activities.'),
        'commands': {
            'get-identities': {
                'help': 'Inspect Globus Auth Identities',
                'func': auth.get_identities,
                'arguments': [
                    (['--usernames'],
                     {'dest': 'usernames', 'default': [], 'nargs': '+',
                      'help': 'Usernames to lookup in Globus Auth'}
                     ),
                    (['--identities'],
                     {'dest': 'identities', 'default': [], 'nargs': '+',
                      'help': 'Identity IDs to lookup in Globus Auth'}
                     )
                ]
            },
            'token-introspect': {
                'help': 'Inspect Globus Auth Tokens',
                'func': auth.token_introspect,
                'arguments': [
                    (['token'], {'help': 'Token to lookup in Globus Auth'})
                ]
            }
        }
    },
    'transfer': {
        'help': ('Interact with Globus Transfer API. '
                 'Used to inspect, modify, and interact with Globus '
                 'Endpoints. Has capabilities to search Endpoints, manage '
                 'Sharing Access via Access Control Lists (ACLs), manage '
                 'Endpoint roles, and do actual Transfer tasks between '
                 'Endpoints.'),
        'commands': {
            'get-endpoint': {
                'help': 'Get a Globus Endpoint document',
                'func': _not_implemented_func,
                'arguments': []
            },
            'update-endpoint': {
                'help': 'Update an Endpoint definition',
                'func': _not_implemented_func,
                'arguments': []
            },
            'create-endpoint': {
                'help': 'Create a new Endpoint',
                'func': _not_implemented_func,
                'arguments': []
            },
            'endpoint-search': {
                'help': 'Search for Globus Endpoints',
                'func': transfer.endpoint_search,
                'arguments': [
                    (['--filter-scope'],
                     {'dest': 'scope', 'default': None,
                      'choices': ('all', 'my-endpoints', 'my-gcp-endpoints',
                                  'recently-used', 'in-use', 'shared-by-me',
                                  'shared-with-me'),
                      'help': ('The set of endpoints to search over. '
                               'Omission is equivalent to "all"')}
                     ),
                    (['--filter-fulltext'],
                     {'dest': 'fulltext', 'default': None,
                      'help': ('Text filter to apply to the selected set of '
                               'endpoints.')}
                     )
                ]
            },
            'endpoint-autoactivate': {
                'help': 'Activate an Endpoint via autoactivation',
                'func': transfer.endpoint_autoactivate,
                'arguments': [
                    (['--endpoint-id'],
                     {'dest': 'endpoint_id', 'required': True,
                      'help': ('ID of the endpoint, typically fetched from '
                               'endpoint-search')}
                     )
                ]
            },
            'task-list': {
                'help': 'List Tasks for the current user',
                'func': transfer.task_list,
                'arguments': []
            },
            'task-event-list': {
                'help': 'List Events for a given Task',
                'func': transfer.task_event_list,
                'arguments': [
                    (['--task-id'],
                     {'dest': 'task_id', 'required': True,
                      'help': ('ID of the task for which you want to list '
                               'events.')}
                     )
                ]
            },
            'ls': {
                'help': 'List the contents of a directory on an endpoint',
                'func': transfer.op_ls,
                'arguments': [
                    (['--endpoint-id'],
                     {'dest': 'endpoint_id', 'required': True,
                      'help': ('ID of the endpoint, typically fetched from '
                               'endpoint-search')}
                     ),
                    (['--path'],
                     {'dest': 'path', 'default': '/',
                      'help': ('Path on the remote endpoint to list. '
                               'Defaults to "/"')}
                     )
                ]
            }
        }
    }
}


def build_command_tree(subparsers):
    """
    Add nexus, auth, and transfer subcommands, their subsubcommands, and
    arguments.
    """
    for command in _COMMAND_TREE:
        tr = _COMMAND_TREE[command]
        parser = subparsers.add_parser(command, help=tr['help'])
        subsubparsers = parser.add_subparsers(
            title='Commands', parser_class=GlobusCLISharedParser, metavar='')
        for subcmd in tr['commands']:
            subtr = tr['commands'][subcmd]
            subcmdparser = subsubparsers.add_parser(subcmd, help=subtr['help'])
            subcmdparser.set_defaults(func=subtr['func'])
            for args, kwargs in subtr['arguments']:
                subcmdparser.add_argument(*args, **kwargs)
