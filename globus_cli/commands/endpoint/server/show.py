import click
from textwrap import dedent

from globus_cli.parsing import common_options, endpoint_id_arg, server_id_arg
from globus_cli.safeio import formatted_print, FORMAT_TEXT_RECORD

from globus_cli.services.transfer import get_client


@click.command('show', help='Show a server belonging to an endpoint')
@common_options
@endpoint_id_arg
@server_id_arg
def server_show(endpoint_id, server_id):
    """
    Executor for `globus endpoint server show`
    """
    client = get_client()

    server_doc = client.get_endpoint_server(endpoint_id, server_id)
    if not server_doc['uri']:  # GCP endpoint server
        fields = (('ID', 'id'),)
        text_epilog = dedent("""
            This server is for a Globus Connect Personal installation.

            For its connection status, try:
            globus endpoint show {}
        """.format(endpoint_id))
    else:
        def advertised_port_summary(server):
            def get_range_summary(start, end):
                return ('unspecified' if not start and not end
                        else 'unrestricted' if start == 1024 and end == 65535
                        else '{}-{}'.format(start, end))

            return "incoming {}, outgoing {}".format(
                       get_range_summary(server['incoming_data_port_start'],
                                         server['incoming_data_port_end']),
                       get_range_summary(server['outgoing_data_port_start'],
                                         server['outgoing_data_port_end']),
                   )

        fields = (('ID', 'id'), ('URI', 'uri'), ('Subject', 'subject'),
                  ('Data Ports', advertised_port_summary))
        text_epilog = None

    formatted_print(server_doc, text_format=FORMAT_TEXT_RECORD,
                    fields=fields, text_epilog=text_epilog)
