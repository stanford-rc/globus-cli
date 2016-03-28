from globus_cli.helpers import cliargs


@cliargs('Not Implemented', [])
def not_implemented_func(args):
    """
    This is a dummy function used to stub parts of the command tree that
    haven't been implemented yet.
    It has the same signature as a typical command function (i.e. takes args
    and nothing else), but raises a NotImplementedError
    """
    raise NotImplementedError(('Hold yer horses! '
                               'This command has not been implemented yet!'))


class MenuCommand(object):
    def __init__(self, name, commandset, helptext=None):
        self.name = name
        self.commandset = commandset
        self.helptext = helptext


class FuncCommand(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.helptext = func.cli_help


def add_cli_args(parser, argset):
    # group required args separately from truly optional ones
    required_args_group = parser.add_argument_group(
        'required arguments')
    for cli_arg in argset:
        args, kwargs = (cli_arg.argparse_arglist(),
                        cli_arg.argparse_kwargs())
        if cli_arg.is_required():
            required_args_group.add_argument(*args, **kwargs)
        else:
            parser.add_argument(*args, **kwargs)
