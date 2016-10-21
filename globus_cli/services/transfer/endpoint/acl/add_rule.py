import click

from globus_cli.parsing import (
    CaseInsensitiveChoice, common_options, ENDPOINT_PLUS_REQPATH)
from globus_cli.helpers import print_json_response

from globus_cli.services.auth import maybe_lookup_identity_id

from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('add-rule', help='Add an ACL rule')
@common_options
@click.option('--permissions', required=True,
              type=CaseInsensitiveChoice(('r', 'rw')),
              help='Permissions to add. Read-Only or Read/Write')
@click.option('--principal', required=True,
              help=('Principal to grant permissions to. ID of a Group or '
                    'Identity, or a valid Identity Name, like '
                    '"go@globusid.org"'))
@click.option('--principal-type', required=True,
              type=CaseInsensitiveChoice(('identity', 'group', 'anonymous',
                                          'all_authenticated_users')),
              help='Principal type to grant permissions to')
@click.argument('endpoint_plus_path', metavar=ENDPOINT_PLUS_REQPATH.metavar,
                type=ENDPOINT_PLUS_REQPATH)
def add_acl_rule(principal_type, principal, permissions, endpoint_plus_path):
    """
    Executor for `globus transfer acl add-rule`
    """
    endpoint_id, path = endpoint_plus_path
    client = get_client()

    if principal_type == 'identity':
        principal = maybe_lookup_identity_id(principal)

    rule_data = assemble_generic_doc(
        'access', permissions=permissions, principal=principal,
        principal_type=principal_type, path=path)

    res = client.add_endpoint_acl_rule(endpoint_id, rule_data)

    print_json_response(res)
