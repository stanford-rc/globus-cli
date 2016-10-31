import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.config import (
    AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME,
    AUTH_AT_OPTNAME, TRANSFER_AT_OPTNAME,
    AUTH_AT_EXPIRES_OPTNAME, TRANSFER_AT_EXPIRES_OPTNAME,
    WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME,
    WHOAMI_EMAIL_OPTNAME, WHOAMI_NAME_OPTNAME,
    internal_auth_client, remove_option, lookup_option)


@click.command('logout',
               short_help=('Logout of Globus, revoking credentials for '
                           'the Globus CLI'),
               help=('Remove credentials for the Globus CLI. '
                     'Effectively stops any use of your CLI credentials as '
                     'well'))
@common_options
def logout_command():
    # build the NativeApp client object
    native_client = internal_auth_client()

    # prompt
    confirmed = click.confirm("Are you sure you'd like to logout?")
    if not confirmed:
        return

    safeprint('Logging out of Globus as {}'
              .format(lookup_option(WHOAMI_USERNAME_OPTNAME)))

    # remove tokens from config and revoke them
    for token_opt in (TRANSFER_RT_OPTNAME, TRANSFER_AT_OPTNAME,
                      TRANSFER_AT_EXPIRES_OPTNAME,
                      AUTH_RT_OPTNAME, AUTH_AT_OPTNAME,
                      AUTH_AT_EXPIRES_OPTNAME):
        token = remove_option(token_opt)
        if token:
            native_client.oauth2_revoke_token(token)
    for whoami_opt in (WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME,
                       WHOAMI_EMAIL_OPTNAME, WHOAMI_NAME_OPTNAME):
        remove_option(whoami_opt)
