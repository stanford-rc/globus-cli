import click

from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.safeio import FORMAT_TEXT_RAW, formatted_print
from globus_cli.services.transfer import get_client


@command("delete")
@endpoint_id_arg
@click.argument("rule_id")
def delete_command(endpoint_id, rule_id):
    """Delete an access control rule, removing permissions"""
    client = get_client()

    res = client.delete_endpoint_acl_rule(endpoint_id, rule_id)
    formatted_print(res, text_format=FORMAT_TEXT_RAW, response_key="message")
