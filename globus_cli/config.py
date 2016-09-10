import globus_sdk
import globus_sdk.config

__all__ = [
    'get_internal_auth_client',
    'get_output_format'
]


# constant for use throughout the SDK whenever we need to do things using the
# CLI Native App definition
CLIENT_ID = '95fdeba8-fac2-42bd-a357-e068d82ff78e'

OUTPUT_FORMAT_OPTNAME = 'output_format'


def lookup_option(option, section='cli'):
    p = globus_sdk.config._get_parser()
    return p.get(option, section=section)


def get_output_format():
    return lookup_option(OUTPUT_FORMAT_OPTNAME)


def get_internal_auth_client():
    return globus_sdk.NativeAppAuthClient(CLIENT_ID)
