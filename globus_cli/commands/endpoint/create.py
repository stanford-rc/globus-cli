import click
import inspect

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
def endpoint_create(endpoint_type, shared, display_name, description,
                    info_link, contact_info, contact_email, organization,
                    department, keywords, public, location, disable_verify,
                    myproxy_dn, myproxy_server, oauth_server, force_encryption,
                    default_directory, subscription_id, network_use,
                    max_concurrency, preferred_concurrency,
                    max_parallelism, preferred_parallelism):
    """
    Executor for `globus endpoint create`
    """
    client = get_client()

    # validate params
    if shared:
        endpoint_type = "shared"
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    params = dict((k, values[k]) for k in args)

    is_globus_connect = params.pop("endpoint_type") == 'personal' or None
    params["is_globus_connect"] = is_globus_connect
    validate_endpoint_create_and_update_params(endpoint_type, False, params)

    # shared endpoint creation
    if shared:
        endpoint_id, host_path = params.pop("shared")
        params["host_endpoint"] = endpoint_id
        params["host_path"] = host_path

        ep_doc = assemble_generic_doc('shared_endpoint', **params)
        autoactivate(client, endpoint_id, if_expires_in=60)
        res = client.create_shared_endpoint(ep_doc)

    # non shared endpoint creation
    else:
        # omit `is_globus_connect` key if not GCP, otherwise include as `True`
        ep_doc = assemble_generic_doc('endpoint', **params)
        res = client.create_endpoint(ep_doc)

    # output
    formatted_print(res, fields=(COMMON_FIELDS + GCP_FIELDS
                    if is_globus_connect else COMMON_FIELDS),
                    text_format=FORMAT_TEXT_RECORD)
