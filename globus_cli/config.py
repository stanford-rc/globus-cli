import globus_sdk.config

OUTPUT_FORMAT_OPTNAME = 'output_format'


def lookup_option(option, section='cli'):
    p = globus_sdk.config._get_parser()
    return p.get(option, section=section)


def get_output_format():
    return lookup_option(OUTPUT_FORMAT_OPTNAME)
