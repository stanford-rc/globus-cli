import os
from configobj import ConfigObj

import globus_sdk
import globus_sdk.config

from globus_cli import version

__all__ = [
    # option name constants
    'OUTPUT_FORMAT_OPTNAME',
    'AUTH_RT_OPTNAME',
    'TRANSFER_RT_OPTNAME',

    'internal_auth_client',

    'get_output_format',
    'get_auth_refresh_token',
    'get_transfer_refresh_token',

    'write_option',
    'lookup_option',
]


# constant for use throughout the SDK whenever we need to do things using the
# CLI Native App definition
# accessed via `internal_auth_client()` -- not exported
CLIENT_ID = '95fdeba8-fac2-42bd-a357-e068d82ff78e'

# constants for global use
OUTPUT_FORMAT_OPTNAME = 'output_format'
AUTH_RT_OPTNAME = 'auth_refresh_token'
TRANSFER_RT_OPTNAME = 'transfer_refresh_token'


def _get_config_obj(system=False):
    # FIXME: DRY violation with config_commands.helpers
    if system:
        path = '/etc/globus.cfg'
    else:
        path = os.path.expanduser("~/.globus.cfg")

    return ConfigObj(path)


def lookup_option(option, section='cli'):
    p = globus_sdk.config._get_parser()
    return p.get(option, section=section)


def write_option(option, value, section='cli', system=False):
    """
    Write an option to disk -- doesn't handle config reloading
    """
    # FIXME: DRY violation with config_commands.helpers
    conf = _get_config_obj(system=system)

    conf[section][option] = value
    conf.write()


def get_output_format():
    return lookup_option(OUTPUT_FORMAT_OPTNAME)


def get_auth_refresh_token():
    return lookup_option(AUTH_RT_OPTNAME)


def get_transfer_refresh_token():
    return lookup_option(TRANSFER_RT_OPTNAME)


def internal_auth_client():
    return globus_sdk.NativeAppAuthClient(CLIENT_ID, app_name=version.app_name)
