import click

from globus_cli.parsing import (
    common_options, endpoint_create_and_update_params, endpoint_id_arg)
from globus_cli.helpers import print_json_response
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('share', help='Create a new Share, hosted on an Endpoint')
@common_options
@endpoint_id_arg(metavar='HOST_ENDPOINT_ID')
@endpoint_create_and_update_params(create=True, shared_ep=True)
def endpoint_create_share(endpoint_id, display_name, description, organization,
                          contact_email, contact_info, info_link):
    """
    Executor for `globus transfer share create`
    """
    ep_doc = assemble_generic_doc(
        'shared_endpoint', host_endpoint_id=endpoint_id,
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link, public=True)

    client = get_client()
    res = client.create_endpoint(ep_doc)
    print_json_response(res)
