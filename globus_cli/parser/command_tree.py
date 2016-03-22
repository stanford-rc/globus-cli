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


_COMMANDS = '__commands__'
_HELP = '__help__'
_FUNC = '__func__'
_ARGUMENTS = '__arguments__'

_COMMAND_TREE = {
    'nexus': {
        _HELP: ('Interact with legacy Nexus API. WARNING: Deprecated. '
                'Only use this if you need access to legacy tokens '
                'during the development of the globus cli. These methods '
                'will be replaced in the near future with commands '
                'which use other services.'),
        _COMMANDS: {
            'get-goauth-token': {
                _HELP: 'Get a Legacy GOAuth Token from Globus Nexus.',
                _FUNC: nexus.get_goauth_token,
                _ARGUMENTS: [
                    (['-u', '--username'],
                     {'dest': 'username', 'default': None,
                      'help': ('Username for a GlobusID user to use to '
                               'get a token.')}
                     ),
                    (['-p', '--password'],
                     {'dest': 'password', 'default': None,
                      'help': ('Password for a GlobusID user to use to '
                               'get a token.')}
                     )
                ]
            }
        }
    },
    'auth': {
        _HELP: ('Interact with Globus Auth API. '
                'Used to inspect tokens, identities, identity sets, '
                'consent to service terms, revoke and manage consents, '
                'manage OAuth Clients, and a variety of other '
                'Authorization and Authentication based activities.'),
        _COMMANDS: {
            'get-identities': {
                _HELP: 'Inspect Globus Auth Identities',
                _FUNC: auth.get_identities,
                _ARGUMENTS: [
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
                _HELP: 'Inspect Globus Auth Tokens',
                _FUNC: auth.token_introspect,
                _ARGUMENTS: [
                    (['token'], {'help': 'Token to lookup in Globus Auth'})
                ]
            }
        }
    },
    'transfer': {
        _HELP: ('Interact with Globus Transfer API. '
                'Used to inspect, modify, and interact with Globus '
                'Endpoints. Has capabilities to search Endpoints, manage '
                'Sharing Access via Access Control Lists (ACLs), manage '
                'Endpoint roles, and do actual Transfer tasks between '
                'Endpoints.'),
        _COMMANDS: {
            'endpoint': {
                _HELP: ('Interact with Globus Endpoint definitions in Globus. '
                        'Display endpoint information, create and update new '
                        'endpoints, and search existing endpoints.'),
                _COMMANDS: {
                    'show': {
                        _HELP: 'Get a Globus Endpoint document',
                        _FUNC: _not_implemented_func,
                        _ARGUMENTS: []
                    },
                    'update': {
                        _HELP: 'Update an Endpoint definition',
                        _FUNC: _not_implemented_func,
                        _ARGUMENTS: []
                    },
                    'create': {
                        _HELP: 'Create a new Endpoint',
                        _FUNC: _not_implemented_func,
                        _ARGUMENTS: []
                    },
                    'search': {
                        _HELP: 'Search for Globus Endpoints',
                        _FUNC: transfer.endpoint_search,
                        _ARGUMENTS: [
                            (['--filter-scope'],
                             {'dest': 'scope', 'default': None,
                              'choices': ('all', 'my-endpoints',
                                          'my-gcp-endpoints', 'recently-used',
                                          'in-use', 'shared-by-me',
                                          'shared-with-me'),
                              'help': ('The set of endpoints to search over. '
                                       'Omission is equivalent to "all"')}
                             ),
                            (['--filter-fulltext'],
                             {'dest': 'fulltext', 'default': None,
                              'help': ('Text filter to apply to the selected '
                                       'set of endpoints.')}
                             )
                        ]
                    },
                    'autoactivate': {
                        _HELP: 'Activate an Endpoint via autoactivation',
                        _FUNC: transfer.endpoint_autoactivate,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             )
                        ]
                    },
                    'server-list': {
                        _HELP: 'List all servers belonging to an Endpoint',
                        _FUNC: transfer.endpoint_server_list,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             )
                        ]
                    },
                    'my-shared-endpoint-list': {
                        _HELP: ('List all Shared Endpoints on an Endpoint '
                                'owned by the current user'),
                        _FUNC: transfer.my_shared_endpoint_list,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             )
                        ]
                    }
                }
            },
            'task': {
                _HELP: ('Manage asynchronous Tasks in Globus. '
                        'File transfers, deletions, and other asynchronous '
                        'fire-and-forget transfers in Globus are represented '
                        'as Task documents. List, inspect, cancel, pause, and '
                        'resume your Tasks using this command.'),
                _COMMANDS: {
                    'list': {
                        _HELP: 'List Tasks for the current user',
                        _FUNC: transfer.task_list,
                        _ARGUMENTS: []
                    },
                    'event-list': {
                        _HELP: 'List Events for a given Task',
                        _FUNC: transfer.task_event_list,
                        _ARGUMENTS: [
                            (['--task-id'],
                             {'dest': 'task_id', 'required': True,
                              'help': ('ID of the task for which you want to '
                                       'list events.')}
                             )
                        ]
                    }
                }
            },
            'access': {
                _HELP: ('Manage and inspect the access and permissions on '
                        'Globus Transfer resources. '
                        'Primarily consists of Endpoint Roles and Endpoint '
                        'ACLs.'),
                _COMMANDS: {
                    'endpoint-role-list': {
                        _HELP: 'List of assigned Roles on an Endpoint',
                        _FUNC: transfer.endpoint_role_list,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             )
                        ]
                    },
                    'endpoint-acl-list': {
                        _HELP: ('List of Access Control List rules on an '
                                'Endpoint'),
                        _FUNC: transfer.endpoint_acl_list,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             )
                        ]
                    }
                }
            },
            'file': {
                _HELP: ('Start asynchronous Tasks, and perform synchronous '
                        'filesystem operations on Endpoints. '
                        'Many Globus capabilities are only available as '
                        'asynchronous actions in which you start a data '
                        'transfer or other activity, and then let Globus '
                        'take control of the minutae. '
                        'Start Tasks with these commands, then poll and '
                        'inspect them with `globus transfer task ...`. '
                        'All asynchronous commands have the prefix "async-" '
                        'and all other commands are synchronous activity.'),
                _COMMANDS: {
                    'async-transfer': {
                        _HELP: ('Copy a file or directory from one endpoint '
                                'to another as an asynchronous task'),
                        _FUNC: transfer.submit_transfer,
                        _ARGUMENTS: [
                            (['--source-endpoint'],
                             {'dest': 'source_endpoint', 'required': True,
                              'help': ('ID of the endpoint from which to '
                                       'transfer')}
                             ),
                            (['--dest-endpoint'],
                             {'dest': 'dest_endpoint', 'required': True,
                              'help': ('ID of the endpoint to which to '
                                       'transfer')}
                             ),
                            (['--source-path'],
                             {'dest': 'source', 'required': True,
                              'help': ('Path to the file/dir to move on '
                                       'source-endpoint')
                              }
                             ),
                            (['--dest-path'],
                             {'dest': 'dest', 'required': True,
                              'help': ('Desired location of the file/dir on '
                                       'dest-endpoint')
                              }
                             )
                        ]
                    },
                    'async-delete': {
                        _HELP: ('Delete a file or directory from one endpoint '
                                'as an asynchronous task'),
                        _FUNC: transfer.submit_delete,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint from which to '
                                       'delete file(s)')}
                             ),
                            (['--path'],
                             {'dest': 'path', 'required': True,
                              'help': 'Path to the file/dir to delete'
                              }
                             ),
                            (['--recursive'],
                             {'dest': 'recursive', 'default': False,
                              'help': 'Recursively delete dirs',
                              'action': 'store_true'
                              }
                             ),
                            (['--ignore-missing'],
                             {'dest': 'ignore_missing', 'default': False,
                              'help': ('Don\'t throw errors if the file or '
                                       'dir is absent'),
                              'action': 'store_true'
                              }
                             )
                        ]
                    },
                    'ls': {
                        _HELP: ('List the contents of a directory on an '
                                'endpoint'),
                        _FUNC: transfer.op_ls,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             ),
                            (['--path'],
                             {'dest': 'path', 'default': '/',
                              'help': ('Path on the remote endpoint to list. '
                                       'Defaults to "/"')}
                             )
                        ]
                    },
                    'mkdir': {
                        _HELP: 'Make a directory on an Endpoint',
                        _FUNC: transfer.op_mkdir,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             ),
                            (['--path'],
                             {'dest': 'path', 'required': True,
                              'help': 'Path on the remote endpoint to create'
                              }
                             )
                        ]
                    },
                    'rename': {
                        _HELP: 'Rename a file or directory on an Endpoint',
                        _FUNC: transfer.op_rename,
                        _ARGUMENTS: [
                            (['--endpoint-id'],
                             {'dest': 'endpoint_id', 'required': True,
                              'help': ('ID of the endpoint, typically fetched '
                                       'from endpoint-search')}
                             ),
                            (['--old-path'],
                             {'dest': 'oldpath', 'required': True,
                              'help': 'Path to the file/dir to rename'
                              }
                             ),
                            (['--new-path'],
                             {'dest': 'newpath', 'required': True,
                              'help': ('Desired location of the file/dir '
                                       'after rename')
                              }
                             )
                        ]
                    }
                }
            },
            'bookmark-list': {
                _HELP: 'List Bookmarks for the current user',
                _FUNC: transfer.bookmark_list,
                _ARGUMENTS: []
            }
        }
    }
}


def _add_subcommands(parser, command_dict):
    subparsers = parser.add_subparsers(
        title='Commands', parser_class=GlobusCLISharedParser, metavar='')

    for command in command_dict:
        current_command = command_dict[command]
        current_parser = subparsers.add_parser(
            command, help=current_command[_HELP])

        if _COMMANDS in current_command:
            _add_subcommands(current_parser, current_command[_COMMANDS])
        else:
            current_parser.set_defaults(func=current_command[_FUNC])
            for args, kwargs in current_command[_ARGUMENTS]:
                current_parser.add_argument(*args, **kwargs)


def build_command_tree():
    """
    Create a parser from the command tree.
    Add nexus, auth, and transfer subcommands, their subsubcommands, and
    arguments.
    """
    top_level_parser = GlobusCLISharedParser()
    _add_subcommands(top_level_parser, _COMMAND_TREE)

    # return the created parser in all of its glory
    return top_level_parser
