import click
import webbrowser

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import outformat_is_json, print_json_response
from globus_cli.config import lookup_option, MYPROXY_USERNAME_OPTNAME
from globus_cli.services.transfer import get_client
from globus_cli.helpers import is_remote_session


@click.command("activate",
               short_help="Activate an endpoint",
               help="""
    Activate an endpoint using Autoactivation, Myproxy, or Web activation.
    Note that since Web and Myproxy activation are mutually exclusive,
    --myproxy-username --myproxy-password and --web are mutually exclusive.

    \b
    Autoactivation will be attempted if no options are given.

    \b
    To use Myproxy activation give both --myproxy-username and
    --myproxy-password. If a default myproxy username has been configured with
    "globus config init" or "globus config set cli.default_myproxy_username"
    only --myproxy-password is required. Note that this is not
    "OAuth for MyProxy" activation which requires Web activation.

    \b
    To use Web activation use the --web option. The CLI will try to open your
    default browser to the endpoint's activation page, but if a remote CLI
    session is detected, or the --no-browser option is given, a url will
    be printed for you to manually follow and activate the endpoint.""")
@common_options
@endpoint_id_arg
@click.option(
    "--myproxy-username", "-U",
    help=("Your username on the endpoint for Myproxy activation. Note, this "
          "is not necessarily your globus username. Mutually exclusive with "
          "--web. Requires --myproxy-password. Overrides any myproxy-username "
          "in config."))
@click.option(
    "--myproxy-password", "-P",
    help=("Your password on the endpoint for Myproxy activation. Note, this "
          "should not be your globus password. Mutually exclusive with "
          "--web. Requires --myproxy-username or cli.default_myproxy_username "
          "to be set in config."))
@click.option("--web", is_flag=True, default=False,
              help=("Use web activation. Mutually exclusive with "
                    "--myproxy-username and --myproxy-password"))
@click.option("--no-browser", is_flag=True, default=False,
              help=("If using --web, Give a url to manually follow instead of "
                    "opening your default web browser. Implied if on a "
                    "remote session."))
def endpoint_activate(endpoint_id, myproxy_username, myproxy_password,
                      web, no_browser):
    """
    Executor for `globus endpoint activate`
    """
    default_myproxy_username = lookup_option(MYPROXY_USERNAME_OPTNAME)
    client = get_client()

    # validate options
    if web and (myproxy_password or myproxy_username):
        raise click.UsageError(
            "--web is mutually exclusive with "
            "--myproxy-password and --myproxy-username")
    if myproxy_password and not (myproxy_username or default_myproxy_username):
        raise click.UsageError(
            "--myproxy-password requires either --myproxy-username or "
            "cli.default_myproxy_username to be set in config")
    if no_browser and not web:
        raise click.UsageError("--no-browser requires --web")

    # myproxy activation
    if myproxy_password:

        no_server_msg = ("This endpoint has no myproxy server "
                         "and so cannot be activated through myproxy")
        requirements_data = client.endpoint_get_activation_requirements(
            endpoint_id).data

        if not len(requirements_data["DATA"]):
            raise click.ClickException(no_server_msg)

        for data in requirements_data["DATA"]:
            if data["name"] == "passphrase":
                data["value"] = myproxy_password
            if data["name"] == "username":
                data["value"] = myproxy_username or default_myproxy_username
            if data["name"] == "hostname" and data["value"] is None:
                raise click.ClickException(no_server_msg)

        res = client.endpoint_activate(endpoint_id, requirements_data)

    # web activation
    elif web:
        url = ("https://www.globus.org/app/"
               "endpoints/{}/activate".format(endpoint_id))
        if no_browser or is_remote_session():
            res = {"message": "Web activation url: {}".format(url),
                   "url": url}
        else:
            webbrowser.open(url, new=1)
            res = {"message": "Browser opened to web activation page",
                   "url": url}

    # autoactivation
    else:
        res = client.endpoint_autoactivate(endpoint_id)

    # output
    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res["message"])
