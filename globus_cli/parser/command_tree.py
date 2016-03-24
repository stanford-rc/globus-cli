from globus_cli.parser.shared_parser import GlobusCLISharedParser
from globus_cli.services import nexus, auth, transfer
from globus_cli.helpers import cliargs


@cliargs('Not Implemented', [])
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
_FUNC = '__func__'
_HELP = '__help__'


_NEXUS_COMMANDS = {
    'get-goauth-token': {
        _FUNC: nexus.get_goauth_token
    }
}

_AUTH_COMMANDS = {
    'get-identities': {
        _FUNC: auth.get_identities
    },
    'token-introspect': {
        _FUNC: auth.token_introspect
    }
}

_TRANSFER_COMMANDS = {
    'endpoint': {
        _HELP: ('Interact with Globus Endpoint definitions in Globus. '
                'Display endpoint information, create and update new '
                'endpoints, and search existing endpoints.'),
        _COMMANDS: {
            'show': {
                _FUNC: _not_implemented_func
            },
            'update': {
                _FUNC: _not_implemented_func
            },
            'create': {
                _FUNC: _not_implemented_func
            },
            'search': {
                _FUNC: transfer.endpoint_search
            },
            'autoactivate': {
                _FUNC: transfer.endpoint_autoactivate
            },
            'deactivate': {
                _FUNC: transfer.endpoint_deactivate
            },
            'server-list': {
                _FUNC: transfer.endpoint_server_list
            },
            'my-shared-endpoint-list': {
                _FUNC: transfer.my_shared_endpoint_list
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
                _FUNC: transfer.task_list
            },
            'event-list': {
                _FUNC: transfer.task_event_list
            },
            'pause-info': {
                _FUNC: transfer.task_pause_info
            },
            'cancel': {
                _FUNC: transfer.cancel_task
            },
            'update': {
                _FUNC: transfer.update_task
            },
            'show': {
                _FUNC: transfer.show_task
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
                _FUNC: transfer.endpoint_role_list
            },
            'acl-list': {
                _FUNC: transfer.acl_list
            },
            'show-acl-rule': {
                _FUNC: transfer.show_acl_rule
            },
            'add-acl-rule': {
                _FUNC: transfer.add_acl_rule
            },
            'del-acl-rule': {
                _FUNC: transfer.del_acl_rule
            },
            'update-acl-rule': {
                _FUNC: transfer.update_acl_rule
            }
        }
    },
    'async-transfer': {
        _FUNC: transfer.submit_transfer
    },
    'async-delete': {
        _FUNC: transfer.submit_delete
    },
    'ls': {
        _FUNC: transfer.op_ls
    },
    'mkdir': {
        _FUNC: transfer.op_mkdir
    },
    'rename': {
        _FUNC: transfer.op_rename
    },
    'bookmark-list': {
        _FUNC: transfer.bookmark_list
    }
}

_COMMAND_TREE = {
    'nexus': {
        _HELP: ('Interact with legacy Nexus API. WARNING: Deprecated. '
                'Only use this if you need access to legacy tokens '
                'during the development of the globus cli. These methods '
                'will be replaced in the near future with commands '
                'which use other services.'),
        _COMMANDS: _NEXUS_COMMANDS
    },
    'auth': {
        _HELP: ('Interact with Globus Auth API. '
                'Used to inspect tokens, identities, identity sets, '
                'consent to service terms, revoke and manage consents, '
                'manage OAuth Clients, and a variety of other '
                'Authorization and Authentication based activities.'),
        _COMMANDS: _AUTH_COMMANDS
    },
    'transfer': {
        _HELP: ('Interact with Globus Transfer API. '
                'Used to inspect, modify, and interact with Globus '
                'Endpoints. Has capabilities to search Endpoints, manage '
                'Sharing Access via Access Control Lists (ACLs), manage '
                'Endpoint roles, and do actual Transfer tasks between '
                'Endpoints.'),
        _COMMANDS: _TRANSFER_COMMANDS
    }
}


def _add_subcommands(parser, command_dict):
    def gethelp(maybe_command):
        if _FUNC in maybe_command:
            return maybe_command[_FUNC].cli_help
        else:
            return maybe_command[_HELP]

    subparsers = parser.add_subparsers(
        title='Commands', parser_class=GlobusCLISharedParser, metavar='')

    for command in command_dict:
        current_command = command_dict[command]
        current_parser = subparsers.add_parser(
            command, help=gethelp(current_command))

        if _COMMANDS in current_command:
            _add_subcommands(current_parser, current_command[_COMMANDS])
        else:
            current_parser.set_defaults(func=current_command[_FUNC])
            required_args_group = current_parser.add_argument_group(
                'required arguments')
            for args, kwargs in current_command[_FUNC].cli_arguments:
                if 'required' in kwargs and kwargs['required']:
                    required_args_group.add_argument(*args, **kwargs)
                else:
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
