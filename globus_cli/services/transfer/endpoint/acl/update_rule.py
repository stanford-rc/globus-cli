import click

from globus_cli.parsing import (
    CaseInsensitiveChoice, common_options, EndpointPlusPath)
from globus_cli.helpers import print_json_response

from globus_cli.services.auth import maybe_lookup_identity_id

from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)

path_type = EndpointPlusPath(path_required=False)


@click.command('update-rule', help='Update an ACL rule')
@common_options
@click.option('--rule-id', required=True, help='ID of the rule to modify')
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
@click.argument('endpoint_plus_path', metavar=path_type.metavar,
                type=path_type)
def update_acl_rule(principal_type, principal, permissions, rule_id,
                    endpoint_plus_path):
    """
    Executor for `globus transfer access update-acl-rule`
    """
    endpoint_id, path = endpoint_plus_path
    client = get_client()

    rule_data = assemble_generic_doc(
        'access', permissions=permissions,
        principal=maybe_lookup_identity_id(principal),
        principal_type=principal_type, path=path)

    res = client.update_endpoint_acl_rule(endpoint_id, rule_id,
                                          rule_data)

    print_json_response(res)
