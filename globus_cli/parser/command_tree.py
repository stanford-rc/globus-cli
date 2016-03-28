import textwrap

from globus_cli.parser.shared_parser import GlobusCLISharedParser
from globus_cli.parser.helpers import (
    not_implemented_func, FuncCommand, MenuCommand, add_cli_args)
from globus_cli.services import nexus, auth, transfer


_NEXUS_COMMANDS = [
    FuncCommand('get-goauth-token', nexus.get_goauth_token)
]

_AUTH_COMMANDS = [
    FuncCommand('get-identities', auth.get_identities),
    FuncCommand('token-introspect', auth.token_introspect)
]

_TRANSFER_COMMANDS = [
    MenuCommand('endpoint', [
        FuncCommand('show', not_implemented_func),
        FuncCommand('update', not_implemented_func),
        FuncCommand('create', not_implemented_func),
        FuncCommand('search', transfer.endpoint_search),
        FuncCommand('autoactivate', transfer.endpoint_autoactivate),
        FuncCommand('deactivate', transfer.endpoint_deactivate),
        FuncCommand('server-list', transfer.endpoint_server_list),
        FuncCommand('my-shared-endpoint-list',
                    transfer.my_shared_endpoint_list)],
                helptext=(
        'Interact with Globus Endpoint definitions in Globus. '
        'Display endpoint information, create and update new '
        'endpoints, and search existing endpoints.')),

    MenuCommand('task', [
        FuncCommand('list', transfer.task_list),
        FuncCommand('event-list', transfer.task_event_list),
        FuncCommand('pause-info', transfer.task_pause_info),
        FuncCommand('cancel', transfer.cancel_task),
        FuncCommand('update', transfer.update_task),
        FuncCommand('show', transfer.show_task)
        ],
                helptext=(
        'Manage asynchronous Tasks in Globus. '
        'File transfers, deletions, and other asynchronous '
        'fire-and-forget transfers in Globus are represented '
        'as Task documents. List, inspect, cancel, pause, and '
        'resume your Tasks using this command.')),

    MenuCommand('access', [
        FuncCommand('endpoint-role-list', transfer.endpoint_role_list),
        FuncCommand('acl-list', transfer.acl_list),
        FuncCommand('show-acl-rule', transfer.show_acl_rule),
        FuncCommand('add-acl-rule', transfer.add_acl_rule),
        FuncCommand('del-acl-rule', transfer.del_acl_rule),
        FuncCommand('update-acl-rule', transfer.update_acl_rule)
        ],
                helptext=(
        'Manage and inspect the access and permissions on '
        'Globus Transfer resources. '
        'Primarily consists of Endpoint Roles and Endpoint '
        'ACLs.')),

    FuncCommand('async-transfer', transfer.submit_transfer),
    FuncCommand('async-delete', transfer.submit_delete),
    FuncCommand('ls', transfer.op_ls),
    FuncCommand('mkdir', transfer.op_mkdir),
    FuncCommand('rename', transfer.op_rename),
    FuncCommand('bookmark-list', transfer.bookmark_list)
]

_COMMAND_TREE = [
    MenuCommand('nexus', _NEXUS_COMMANDS, helptext=(
                'Interact with legacy Nexus API. WARNING: Deprecated. '
                'Only use this if you need access to legacy tokens '
                'during the development of the globus cli. These methods '
                'will be replaced in the near future with commands '
                'which use other services.')),
    MenuCommand('auth', _AUTH_COMMANDS, helptext=(
                'Interact with Globus Auth API. '
                'Used to inspect tokens, identities, identity sets, '
                'consent to service terms, revoke and manage consents, '
                'manage OAuth Clients, and a variety of other '
                'Authorization and Authentication based activities.')),
    MenuCommand('transfer', _TRANSFER_COMMANDS, helptext=(
                'Interact with Globus Transfer API. '
                'Used to inspect, modify, and interact with Globus '
                'Endpoints. Has capabilities to search Endpoints, manage '
                'Sharing Access via Access Control Lists (ACLs), manage '
                'Endpoint roles, and do actual Transfer tasks between '
                'Endpoints.'))
]


def _add_subcommands(parser, commandset):
    """
    Build out subcommands recursively with this helper method.
    Any given command may have subcommands, ad infinitum, so the simplest
    solution is the recursive one.
    Walk commands, plugging in any that terminate the command tree at a
    function. Any others are menu commands that have further subcommands, and
    those therefore require that we add whatever subcommands they have
    (recursive case).
    """

    # we start with a subparser collection named "Commands"
    subparsers = parser.add_subparsers(
        title='Commands', parser_class=GlobusCLISharedParser,
        metavar='')

    # iterate over all commands in the set, and ...
    for command in commandset:
        current_parser = subparsers.add_parser(
            command.name, help=command.helptext)

        # the command wraps a function, build it out
        if isinstance(command, FuncCommand):
            # round up the arguments dangling off of the command and put them
            # in here
            current_parser.set_defaults(func=command.func)
            add_cli_args(current_parser, command.func.cli_arguments)

        # it's a menu, recurse
        else:
            _add_subcommands(current_parser, command.commandset)


def build_command_tree():
    """
    Create a parser from the command tree.
    Add nexus, auth, and transfer subcommands, their subsubcommands, and
    arguments.
    """
    # TODO: Update this description to be more informative, accurate
    description = textwrap.dedent("""Run a globus command.
    The globus command is structured to provide a uniform command line
    interface to all Globus services. For more information and tutorials,
    see docs.globus.org
    """)

    top_level_parser = GlobusCLISharedParser(description=description)
    _add_subcommands(top_level_parser, _COMMAND_TREE)

    # return the created parser in all of its glory
    return top_level_parser
