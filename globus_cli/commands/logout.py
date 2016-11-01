import click
import globus_sdk

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.config import (
    AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME,
    AUTH_AT_OPTNAME, TRANSFER_AT_OPTNAME,
    AUTH_AT_EXPIRES_OPTNAME, TRANSFER_AT_EXPIRES_OPTNAME,
    WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME,
    WHOAMI_EMAIL_OPTNAME, WHOAMI_NAME_OPTNAME,
    internal_auth_client, remove_option, lookup_option)


_RESCIND_HELP = """\
Rescinding Consents
-------------------
The logout command only revokes tokens that it can see in its storage.
If you are concerned that logout may have failed to revoke a token,
you may want to manually rescind the Globus CLI consent on the
Manage Consents Page:
    https://auth.globus.org/consents

"""


_LOGOUT_EPILOG = """\
\nYou are now successfully logged out of the Globus CLI.
Before attempting any further CLI commands, you will have to login again using

  globus login

"""


@click.command('logout',
               short_help='Logout of the Globus CLI',
               help=('Logout of the Globus CLI. '
                     'Removes your Globus tokens from local storage, '
                     'and revokes them so that they cannot be used anymore'))
@common_options(no_format_option=True, no_map_http_status_option=True)
@click.option('--yes', help='Automatically say "Yes" to all prompts',
              is_flag=True, default=False)
def logout_command(yes):
    def _confirm(prompt, default=False):
        """
        Handy confirmation prompt that respects --yes and exits if confirmation
        fails.
        """
        if yes:
            return
        confirmed = click.confirm(prompt, default=default)
        if not confirmed:
            click.get_current_context().exit(1)

    # prompt
    _confirm("Are you sure you'd like to logout?")

    # check for username -- if not set, probably not logged in
    username = lookup_option(WHOAMI_USERNAME_OPTNAME)
    if not username:
        _confirm(("Your username is not set. You may not be logged in. "
                  "Would you like to try to logout anyway?"), default=True)
    safeprint('Logging out of Globus{}\n'.format(' as ' + username
                                                 if username else ''))

    # build the NativeApp client object
    native_client = internal_auth_client()

    # remove tokens from config and revoke them
    # also, track whether or not we should print the rescind help
    print_rescind_help = False
    for token_opt in (TRANSFER_RT_OPTNAME, TRANSFER_AT_OPTNAME,
                      AUTH_RT_OPTNAME, AUTH_AT_OPTNAME):
        # first lookup the token -- if not found we'll continue
        token = lookup_option(token_opt)
        if not token:
            safeprint(('Warning: Found no token named "{}"! '
                       'Recommend rescinding consent').format(token_opt))
            print_rescind_help = True
            continue
        # token was found, so try to revoke it
        try:
            native_client.oauth2_revoke_token(token)
        # if we network error, revocation failed -- print message and abort so
        # that we can revoke later when the network is working
        except globus_sdk.NetworkError:
            safeprint(('Failed to reach Globus to revoke tokens. '
                       'Because we cannot revoke these tokens, cancelling '
                       'logout'))
            click.get_current_context().exit(1)
        # finally, we revoked, so it's safe to remove the token
        remove_option(token_opt)

    # remove expiration times, just for cleanliness
    for expires_opt in (TRANSFER_AT_EXPIRES_OPTNAME,
                        AUTH_AT_EXPIRES_OPTNAME):
        remove_option(expires_opt)

    # remove whoami data
    for whoami_opt in (WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME,
                       WHOAMI_EMAIL_OPTNAME, WHOAMI_NAME_OPTNAME):
        remove_option(whoami_opt)

    safeprint(_LOGOUT_EPILOG)

    # if some token wasn't found in the config, it means its possible that the
    # config file was removed without logout
    # in that case, the user should rescind the CLI consent to invalidate any
    # potentially leaked refresh tokens, so print the help on that
    if print_rescind_help:
        safeprint(_RESCIND_HELP)
