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


def endpoint_create_and_update_params(*args, **kwargs):
    """
    Collection of options consumed by Transfer endpoint create and update
    operations -- in addition to shared endpoint create and update.
    It accepts toggles regarding create vs. update and shared EP vs. normal EP

    Importantly, when given `shared_ep=True`, the options it applies are more
    limited -- so the signature of the decorated function is different.

    Usage:

    >>> @endpoint_create_and_update_params
    >>> def command_func(display_name, description, organization,
    >>>                  contact_email, contact_info, info_link, public,
    >>>                  default_directory, force_encryption, oauth_server,
    >>>                  myproxy_server, myproxy_dn):
    >>>     ...

    or

    >>> @endpoint_create_and_update_params(create=False)
    >>> def command_func(display_name, description, organization,
    >>>                  contact_email, contact_info, info_link, public,
    >>>                  default_directory, force_encryption, oauth_server,
    >>>                  myproxy_server, myproxy_dn):
    >>>     ...

    or

    >>> @endpoint_create_and_update_params(shared_ep=True)
    >>> def command_func(display_name, description, organization,
    >>>                  contact_email, contact_info, info_link, public):
    >>>     ...
    """
    def apply_non_shared_params(f):
        f = click.option(
            '--myproxy-dn',
            help=('Only available on Globus Connect Server. '
                  'Set the MyProxy Server DN'))(f)
        f = click.option(
            '--myproxy-server',
            help=('Only available on Globus Connect Server. '
                  'Set the MyProxy Server URI'))(f)
        f = click.option(
            '--oauth-server',
            help=('Only available on Globus Connect Server. '
                  'Set the OAuth Server URI'))(f)
        f = click.option(
            '--force-encryption/--no-force-encryption', default=None,
            help=('Only available on Globus Connect Server. '
                  '(Un)Force transfers to use encryption'))(f)
        f = click.option(
            '--default-directory',
            help=('Only available on Globus Connect Server. '
                  'Set the default directory'))(f)
        f = click.option(
            '--public/--private', 'public',
            help='Set the Endpoint to be public or private')(f)

        return f

    def inner_decorator(f, create=False, shared_ep=False):
        update_help_prefix = (not create and 'New ') or ''

        ep_or_share = 'Share'
        if not shared_ep:
            ep_or_share = 'Endpoint'
            f = apply_non_shared_params(f)
        f = click.option(
            '--info-link',
            help=(update_help_prefix +
                  'Link for Info about the {0}'.format(ep_or_share)))(f)
        f = click.option(
            '--contact-info',
            help=(update_help_prefix +
                  'Contact Info for the {0}'.format(ep_or_share)))(f)
        f = click.option(
            '--contact-email',
            help=(update_help_prefix +
                  'Contact Email for the {0}'.format(ep_or_share)))(f)
        f = click.option(
            '--organization',
            help=(update_help_prefix +
                  'Organization for the {0}'.format(ep_or_share)))(f)
        f = click.option(
            '--description',
            help=(update_help_prefix +
                  'Description for the {0}'.format(ep_or_share)))(f)
        if create:
            f = click.argument('display_name')(f)
        else:
            f = click.option(
                '--display-name',
                help=(update_help_prefix +
                      'Name for the {0}'.format(ep_or_share)))(f)
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


def role_id_arg(f):
    """
    Unmodifiable `ROLE_ID` argument for Transfer Endpoint Role management.
    """
    return click.argument('role_id')(f)


def server_id_arg(f):
    """
    Unmodifiable `SERVER_ID` argument for Transfer Endpoint Server management.
    """
    return click.argument('server_id')(f)


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


def security_principal_opts(*args, **kwargs):
    def preprocess_security_principals(f):
        def decorator(*args, **kwargs):
            identity = kwargs.pop('identity', None)
            group = kwargs.pop('group', None)
            if kwargs.get('principal') is not None:
                if identity or group:
                    raise click.UsageError(
                        'You may only pass one security principal')
            else:
                if identity and group:
                    raise click.UsageError(
                        ('You have passed both an identity and a group. '
                         'Please only pass one principal type'))
                elif not identity and not group:
                    raise click.UsageError(
                        ('You must provide at least one principal '
                         '(identity, group, etc.)'))

                if identity:
                    kwargs['principal'] = ('identity', identity)
                else:
                    kwargs['principal'] = ('group', group)

            return f(*args, **kwargs)
        return decorator

    def inner_decorator(
            f, allow_anonymous=False, allow_all_authenticated=False):

        # order matters here -- the preprocessor must run after option
        # application, so it has to be applied first
        if isinstance(f, click.Command):
            # if we're decorating a command, put the preprocessor on its
            # callback, not on `f` itself
            f.callback = preprocess_security_principals(f.callback)
        else:
            # otherwise, we're applying to a function, but other decorators may
            # have been applied to give it params
            # so, copy __click_params__ to preserve those parameters
            oldfun = f
            f = preprocess_security_principals(f)
            f.__click_params__ = getattr(oldfun, '__click_params__', [])

        f = click.option('--identity', metavar='IDENTITY_ID_OR_NAME',
                         help='Identity to use as a security principal')(f)
        f = click.option('--group', metavar='GROUP_ID',
                         help='Group to use as a security principal')(f)

        if allow_anonymous:
            f = click.option(
                '--anonymous', 'principal', flag_value=('anonymous', ""),
                help=('Allow anyone access, even without logging in '
                      '(treated as a security principal)'))(f)
        if allow_all_authenticated:
            f = click.option(
                '--all-authenticated', 'principal',
                flag_value=('all_authenticated_users', ""),
                help=('Allow anyone access, as long as they login'
                      '(treated as a security principal)'))(f)

        return f

    return detect_and_decorate(inner_decorator, args, kwargs)
