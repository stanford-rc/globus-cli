import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.safeio import formatted_print

from globus_cli.services.auth import LazyIdentityMap

from globus_cli.services.transfer import get_client


@click.command('list', help='List of assigned roles on an endpoint')
@common_options
@endpoint_id_arg
def role_list(endpoint_id):
    """
    Executor for `globus access endpoint-role-list`
    """
    client = get_client()
    roles = client.endpoint_role_list(endpoint_id)

    resolved_ids = LazyIdentityMap(
        x['principal'] for x in roles if x['principal_type'] == 'identity')

    def principal_str(role):
        principal = role['principal']
        if role['principal_type'] == 'identity':
            username = resolved_ids.get(principal)
            return username or principal
        elif role['principal_type'] == 'group':
            return (u'https://www.globus.org/app/groups/{}').format(principal)
        else:
            return principal

    formatted_print(roles, fields=[
        ('Principal Type', 'principal_type'), ('Role ID', 'id'),
        ('Principal', principal_str), ('Role', 'role')])
