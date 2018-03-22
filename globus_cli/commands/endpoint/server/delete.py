from textwrap import dedent
import click

from globus_cli.parsing import (
    common_options, endpoint_id_arg, CaseInsensitiveChoice)
from globus_cli.safeio import formatted_print, FORMAT_TEXT_RAW

from globus_cli.services.transfer import get_client, get_endpoint_w_server_list


def _spec_to_matches(server_list, server_spec, style):
    """
    style is in {uri, hostname, hostname_port}

    A list of matching server docs.
    Should usually be 0 or 1 matches. Multiple matches are possible though.
    """
    assert style in ('uri', 'hostname', 'hostname_port')

    def match(server_doc):
        if style == 'hostname':
            return server_spec == server_doc['hostname']
        elif style == 'hostname_port':
            return (server_spec == '{}:{}'.format(
                        server_doc['hostname'],
                        server_doc['port']))
        elif style == 'uri':
            return (server_spec == '{}://{}:{}'.format(
                        server_doc['scheme'],
                        server_doc['hostname'],
                        server_doc['port']))
        else:
            raise NotImplementedError(
                'Unreachable error! Something is very wrong.')

    return [server_doc for server_doc in server_list
            if match(server_doc)]


@click.command('delete', help='Delete a server belonging to an endpoint')
@common_options
@endpoint_id_arg
@click.argument('server')
@click.option('--mode', default='id',
              type=CaseInsensitiveChoice(('id', 'hostname', 'uri')),
              help=("""\
    How to interpret the 'server' argument. If multiple servers match, an error
    will be thrown.

    \b
    id: the server ID, as shown in 'globus endpoint server list' (default)

    hostname: the hostname of the server. May also include the port in
    HOSTNAME:PORT notation

    uri: the full server uri, in the form of SCHEME://HOSTNAME:PORT
    """))
def server_delete(endpoint_id, server, mode):
    """
    Executor for `globus endpoint server show`
    """
    client = get_client()

    if mode != 'id':
        style = mode
        if mode == 'hostname' and ':' in server:
            style = 'hostname_port'

        endpoint, server_list = get_endpoint_w_server_list(endpoint_id)

        matches = _spec_to_matches(server_list, server, style)
        if not matches:
            raise click.UsageError('No server was found matching "{}"'
                                   .format(server))
        elif len(matches) > 1:
            raise click.UsageError(dedent("""\
                Multiple servers matched "{}":
                    {}
            """).format(server, [x['id'] for x in server_list]))
        else:
            server = matches[0]['id']

    response = client.delete_endpoint_server(endpoint_id, server)

    formatted_print(response, text_format=FORMAT_TEXT_RAW,
                    response_key='message')
