import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer import get_client


@click.command('del-rule', help='Remove an ACL rule')
@common_options
@endpoint_id_arg
@click.argument('rule_id')
def del_acl_rule(endpoint_id, rule_id):
    """
    Executor for `globus acl del-rule`
    """
    client = get_client()

    res = client.delete_endpoint_acl_rule(endpoint_id, rule_id)

    print_json_response(res)
