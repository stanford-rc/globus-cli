import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.safeio import formatted_print
from globus_cli.helpers import outformat_is_text
from globus_cli.services.auth import get_auth_client
from globus_cli.services.transfer import get_client

_id_batch_size = 100


def _resolve_identities(rules):
    """
    Batch resolve identities to usernames.
    Used only for text-output to get a nice listing.

    Returns a dict mapping IDs to usernames.
    """
    to_resolve = set()
    for rule in rules:
        if rule['principal_type'] == 'identity':
            to_resolve.add(rule['principal'])
    to_resolve = list(to_resolve)

    ac = get_auth_client()
    resolved_map = {}
    for i in range(0, len(to_resolve), _id_batch_size):
        chunk = to_resolve[i:i+_id_batch_size]
        resolved_result = ac.get_identities(ids=chunk)
        for x in resolved_result['identities']:
            resolved_map[x['id']] = x['username']

    return resolved_map


@click.command('list', help='List of permissions on an endpoint')
@common_options
@endpoint_id_arg
def list_command(endpoint_id):
    """
    Executor for `globus endpoint permission list`
    """
    client = get_client()

    rules = client.endpoint_acl_list(endpoint_id)

    resolved_map = {}
    if outformat_is_text():
        resolved_map = _resolve_identities(rules)

    def principal_str(rule):
        principal = rule['principal']
        if rule['principal_type'] == 'identity':
            username = resolved_map.get(rule['principal'])

            return username or principal
        elif rule['principal_type'] == 'group':
            return (u'https://www.globus.org/app/groups/{}'
                    ).format(principal)
        else:
            principal = rule['principal_type']

        return principal

    formatted_print(
        rules, fields=[('Rule ID', 'id'), ('Permissions', 'permissions'),
                       ('Shared With', principal_str), ('Path', 'path')])
