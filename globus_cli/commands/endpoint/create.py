import click

from globus_cli.parsing import (
    common_options, endpoint_create_and_update_params,
    validate_endpoint_create_and_update_params, ENDPOINT_PLUS_REQPATH)
from globus_cli.services.transfer import (
    autoactivate, get_client, assemble_generic_doc)
from globus_cli.safeio import formatted_print, FORMAT_TEXT_RECORD


COMMON_FIELDS = [
    ('Message', 'message'),
    ('Endpoint ID', 'id'),
]

GCP_FIELDS = [
    ('Setup Key', 'globus_connect_setup_key'),
]


@click.command('create', help='Create a new Endpoint')
@common_options
@endpoint_create_and_update_params(create=True)
@click.option('--globus-connect-server', 'endpoint_type', flag_value='server',
              help='This endpoint is a Globus Connect Server endpoint')
@click.option('--globus-connect-personal', 'endpoint_type',
              flag_value='personal', default=True, show_default=True,
              help='This endpoint is a Globus Connect Personal endpoint')
@click.option("--shared", default=None, type=ENDPOINT_PLUS_REQPATH,
              metavar=ENDPOINT_PLUS_REQPATH.metavar,
              help=("This endpoint is a shared endpoint hosted "
                    "on the given endpoint and path"))
def endpoint_create(**kwargs):
    """
    Executor for `globus endpoint create`
    """
    client = get_client()

    # validate options
    endpoint_type = kwargs.pop("endpoint_type")
    shared = kwargs.pop("shared")
    if shared:  # shared overwrites personal or server endpoint types
        endpoint_type = "shared"

    is_globus_connect = endpoint_type == "personal" or None
    kwargs["is_globus_connect"] = is_globus_connect
    validate_endpoint_create_and_update_params(endpoint_type, False, kwargs)

    # shared endpoint creation
    if shared:
        endpoint_id, host_path = shared
        kwargs["host_endpoint"] = endpoint_id
        kwargs["host_path"] = host_path

        ep_doc = assemble_generic_doc('shared_endpoint', **kwargs)
        autoactivate(client, endpoint_id, if_expires_in=60)
        res = client.create_shared_endpoint(ep_doc)

    # non shared endpoint creation
    else:
        # omit `is_globus_connect` key if not GCP, otherwise include as `True`
        ep_doc = assemble_generic_doc('endpoint', **kwargs)
        res = client.create_endpoint(ep_doc)

    # output
    formatted_print(res, fields=(COMMON_FIELDS + GCP_FIELDS
                    if is_globus_connect else COMMON_FIELDS),
                    text_format=FORMAT_TEXT_RECORD)
