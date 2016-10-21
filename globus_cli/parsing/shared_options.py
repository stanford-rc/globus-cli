import click

from globus_cli.version import get_versions
from globus_cli.parsing.command_state import (
    format_option, debug_option, map_http_status_option)
from globus_cli.parsing.case_insensitive_choice import CaseInsensitiveChoice
from globus_cli.parsing.detect_and_decorate import detect_and_decorate


def version_option(f):
    """
    Largely a custom clone of click.version_option -- almost identical, but
    makes more assumptions and prints our special output.
    """
    def callback(ctx, param, value):
        # copied from click.decorators.version_option
        # no idea what resilient_parsing means, but...
        if not value or ctx.resilient_parsing:
            return

        latest, current = get_versions()
        click.echo(('Installed Version: {0}\n'
                    'Latest Version:    {1}\n'
                    '\n{2}').format(
                        current, latest,
                        'You are running the latest version of the Globus CLI'
                        if current == latest else
                        ('You should update your version of the Globus CLI\n'
                         'Update instructions: '
                         'https://globus.github.io/globus-cli/'
                         '#updating-and-removing')
                        if current < latest else
                        'You are running a preview version of the Globus CLI'
            )
        )
        ctx.exit()

    return click.option('--version', help='Show the version and exit.',
                        is_flag=True, expose_value=False, is_eager=True,
                        callback=callback)(f)


def common_options(*args, **kwargs):
    """
    This is a multi-purpose decorator for applying a "base" set of options
    shared by all commands.
    It can be applied either directly, or given keyword arguments.

    Usage:

    >>> @common_options
    >>> def mycommand(abc, xyz):
    >>>     ...

    or

    >>> @common_options(no_format_option=True)
    >>> def mycommand(abc, xyz):
    >>>     ...
    """
    def decorate(f, **kwargs):
        """
        Work of actually decorating a function -- wrapped in here because we
        want to dispatch depending on how `common_options` is invoked
        """
        f = version_option(f)
        f = debug_option(f)
        f = click.help_option('-h', '--help')(f)

        # if the format option is being allowed, it needs to be applied to `f`
        if not kwargs.get('no_format_option'):
            f = format_option(f)

        # if the --map-http-status option is being allowed, ...
        if not kwargs.get('no_map_http_status_option'):
            f = map_http_status_option(f)

        return f

    return detect_and_decorate(decorate, args, kwargs)


def endpoint_id_arg(*args, **kwargs):
    """
    This is the `ENDPOINT_ID` argument consumed by many Transfer endpoint
    related operations. It accepts alternate metavars for cases when another
    name is desirable (e.x. `SHARE_ID`, `HOST_ENDPOINT_ID`), but can also be
    applied as a direct decorator if no specialized metavar is being passed.

    Usage:

    >>> @endpoint_id_arg
    >>> def command_func(endpoint_id):
    >>>     ...

    or

    >>> @endpoint_id_arg(metavar='HOST_ENDPOINT_ID')
    >>> def command_func(endpoint_id):
    >>>     ...
    """
    def decorate(f, **kwargs):
        """
        Work of actually decorating a function -- wrapped in here because we
        want to dispatch depending on how this is invoked
        """
        metavar = kwargs.get('metavar', 'ENDPOINT_ID')
        f = click.argument('endpoint_id', metavar=metavar, type=click.UUID)(f)
        return f

    return detect_and_decorate(decorate, args, kwargs)


def endpoint_create_and_update_opts(*args, **kwargs):
    """
    Collection of options consumed by Transfer endpoint create and update
    operations -- in addition to shared endpoint create and update.
    It accepts toggles regarding create vs. update and shared EP vs. normal EP

    Importantly, when given `shared_ep=True`, the options it applies are more
    limited -- so the signature of the decorated function is different.

    Usage:

    >>> @endpoint_create_and_update_opts
    >>> def command_func(display_name, description, organization,
    >>>                  contact_email, contact_info, info_link, public,
    >>>                  default_directory, force_encryption, oauth_server,
    >>>                  myproxy_server, myproxy_dn):
    >>>     ...

    or

    >>> @endpoint_create_and_update_opts(create=False)
    >>> def command_func(display_name, description, organization,
    >>>                  contact_email, contact_info, info_link, public,
    >>>                  default_directory, force_encryption, oauth_server,
    >>>                  myproxy_server, myproxy_dn):
    >>>     ...

    or

    >>> @endpoint_create_and_update_opts(shared_ep=True)
    >>> def command_func(display_name, description, organization,
    >>>                  contact_email, contact_info, info_link, public):
    >>>     ...
    """
    def inner_decorator(f, create=False, shared_ep=False):
        def _mkopt(*args, **kwargs):
            # ensure that diffhelp gets removed -- otherwise, click.option
            # will see it and be sad
            if kwargs.pop('diffhelp', False) and not create:
                kwargs['help'] = 'New ' + kwargs['help']

            return click.option(*args, **kwargs)

        ep_or_share = 'Share'
        if not shared_ep:
            ep_or_share = 'Endpoint'
            f = _mkopt('--myproxy-dn',
                       help=('Only available on Globus Connect Server. '
                             'Set the MyProxy Server DN'))(f)
            f = _mkopt('--myproxy-server',
                       help=('Only available on Globus Connect Server. '
                             'Set the MyProxy Server URI'))(f)
            f = _mkopt('--oauth-server',
                       help=('Only available on Globus Connect Server. '
                             'Set the OAuth Server URI'))(f)
            f = _mkopt('--force-encryption/--no-force-encryption',
                       default=None,
                       help=('Only available on Globus Connect Server. '
                             '(Un)Force transfers to use encryption'))(f)
            f = _mkopt('--default-directory',
                       help=('Only available on Globus Connect Server. '
                             'Set the default directory'))(f)
        f = _mkopt('--public/--private', 'public',
                   help='Set the {0} to be public or private'
                   .format(ep_or_share))(f)
        f = _mkopt('--info-link', diffhelp=True,
                   help='Link for Info about the {0}'.format(ep_or_share))(f)
        f = _mkopt('--contact-info', diffhelp=True,
                   help='Contact Info for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--contact-email', diffhelp=True,
                   help='Contact Email for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--organization', diffhelp=True,
                   help='Organization for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--description', diffhelp=True,
                   help='Description for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--display-name', required=create, diffhelp=True,
                   help='Name for the {0}'.format(ep_or_share))(f)
        return f

    return detect_and_decorate(inner_decorator, args, kwargs)

def task_id_arg(*args, **kwargs):
    """
    This is the `TASK_ID` argument consumed by many Transfer Task operations.
    It accept a toggle on whether or not it is required

    Usage:

    >>> @task_id_option
    >>> def command_func(task_id):
    >>>     ...

    or

    >>> @task_id_option(required=False)
    >>> def command_func(task_id):
    >>>     ...

    By default, the task ID is made required; pass `required=False` to the
    decorator arguments to make it optional.
    """
    def inner_decorator(f, required=True):
        f = click.argument('TASK_ID', required=required)(f)
        return f
    return detect_and_decorate(inner_decorator, args, kwargs)


def submission_id_option(f):
    """
    Simple decorator that attaches an option to a command for consuming a
    submission ID, i.e. --submission-id
    """
    f = click.option(
        '--submission-id', help=(
            'Task submission ID, as generated by `globus transfer task '
            'generate-submission-id`. Used for safe resubmission in the '
            'presence of network failures.'))(f)
    return f


def role_id_option(f):
    """
    Unmodifiable `--role-id` option for Transfer Endpoint Role management.
    """
    f = click.option('--role-id', required=True, help='ID of the Role')(f)
    return f


def server_id_option(f):
    """
    Unmodifiable `--server-id` option for Transfer Endpoint Server management.
    """
    f = click.option('--server-id', required=True, help='ID of the Server')(f)
    return f


def server_add_and_update_opts(*args, **kwargs):
    """
    shared collection of options for `globus transfer endpoint server add` and
    `globus transfer endpoint server update`.
    Accepts a toggle to know if it's being used as `add` or `update`.

    usage:

    >>> @server_add_and_update_opts
    >>> def command_func(subject, port, scheme, hostname):
    >>>     ...

    or

    >>> @server_add_and_update_opts(add=True)
    >>> def command_func(subject, port, scheme, hostname):
    >>>     ...
    """
    def inner_decorator(f, add=False):
        f = click.option('--hostname', required=add,
                         help='Server Hostname.')(f)

        default_scheme = 'gsiftp' if add else None
        f = click.option(
            '--scheme', help='Scheme for the Server.',
            type=CaseInsensitiveChoice(('gsiftp', 'ftp')),
            default=default_scheme, show_default=add)(f)

        default_port = 2811 if add else None
        f = click.option(
            '--port', help='Port for Globus control channel connections.',
            type=int, default=default_port, show_default=add)(f)

        f = click.option(
            '--subject',
            help=('Subject of the X509 Certificate of the server. When '
                  'unspecified, the CN must match the server hostname.'))(f)

        return f
    return detect_and_decorate(inner_decorator, args, kwargs)
