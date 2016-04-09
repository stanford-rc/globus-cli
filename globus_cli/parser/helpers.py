from globus_cli.helpers import wrap_helptext

class MenuCommand(object):
    def __init__(self, name, commandset, helptext):
        self.name = name
        self.commandset = commandset
        self.helptext = wrap_helptext(helptext)


class FuncCommand(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.helptext = wrap_helptext(func.cli_help)


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
