import click
import inspect

from globus_cli.safeio import safeprint
from globus_cli.parsing import (
    common_options, endpoint_id_arg, endpoint_create_and_update_params,
    validate_endpoint_create_and_update_params)
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client, assemble_generic_doc


@click.command('update', help='Update attributes of an Endpoint')
@common_options
@endpoint_id_arg
@endpoint_create_and_update_params(create=False)
def endpoint_update(endpoint_id, display_name, description, info_link,
                    contact_info, contact_email, organization, department,
                    keywords, public, location, disable_verify, myproxy_dn,
                    myproxy_server, oauth_server, force_encryption,
                    default_directory, subscription_id, network_use,
                    max_concurrency, preferred_concurrency,
                    max_parallelism, preferred_parallelism):
    """
    Executor for `globus endpoint update`
    """
    # validate params. Requires a get call to check the endpoint type
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    params = dict((k, values[k]) for k in args)

    client = get_client()
    get_res = client.get_endpoint(params.pop("endpoint_id"))

    if get_res["host_endpoint_id"]:
        endpoint_type = "shared"
    elif get_res["is_globus_connect"]:
        endpoint_type = "personal"
    elif get_res["s3_url"]:
        endpoint_type = "s3"
    else:
        endpoint_type = "server"
    validate_endpoint_create_and_update_params(
        endpoint_type, get_res["subscription_id"], params)

    # make the update
    ep_doc = assemble_generic_doc('endpoint', **params)
    res = client.update_endpoint(endpoint_id, ep_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
