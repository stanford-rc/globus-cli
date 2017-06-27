import click
import re

from globus_cli.parsing import common_options, ENDPOINT_PLUS_OPTPATH
from globus_cli.safeio import formatted_print
from globus_cli.helpers import is_verbose, outformat_is_json
from globus_cli.services.transfer import (
    get_client, autoactivate, iterable_response_to_dict)


@click.command('ls', help='List the contents of a directory on an endpoint',
               short_help='List endpoint directory contents')
@common_options
@click.argument('endpoint_plus_path', metavar=ENDPOINT_PLUS_OPTPATH.metavar,
                type=ENDPOINT_PLUS_OPTPATH)
@click.option('--all', '-a', is_flag=True,
              help=('Show files and directories that start with `.`'))
@click.option('--long', '-l', is_flag=True,
              help=('For text output only. Do long form output, kind '
                    'of like `ls -l`'))
@click.option('--recursive', '-r', is_flag=True, show_default=True,
              help=('Do a recursive listing, up to the depth limit. '
                    'Similar to `ls -R`'))
@click.option('--recursive-depth-limit', default=3, show_default=True,
              type=click.IntRange(min=0), metavar='INTEGER',
              help=('Limit to number of directories to traverse in '
                    '`--recursive` listings. A value of 0 indicates that '
                    'this should behave like a non-recursive `ls`'))
def ls_command(endpoint_plus_path, recursive_depth_limit,
               recursive, long, all):
    """
    Executor for `globus ls`
    """
    endpoint_id, path = endpoint_plus_path

    # do autoactivation before the `ls` call so that recursive invocations
    # won't do this repeatedly, and won't have to instantiate new clients
    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    # create the query paramaters to send to operation_ls
    ls_params = {"show_hidden": int(all)}
    if path:
        ls_params["path"] = path

    # get the `ls` result
    if recursive:
        res = client.recursive_operation_ls(
            endpoint_id, depth=recursive_depth_limit, **ls_params)
    else:
        res = client.operation_ls(endpoint_id, **ls_params)

    def formated_item_name(item):
        # determine if the formated item name should end in / or not
        final_slash = ("/" if item["type"] == "dir" else "")

        # ignore any trailing slashes for easier logic
        if path and path[-1] == "/":
            formatted_path = path[:-1]
        else:
            formatted_path = path

        # if the item has a path field, it is recursive, and we want
        # to display the relative path from the start of the ls.
        if item.get("path"):

            # if the ls command has a starting path,
            # give everything relative to that path
            if formatted_path:
                relative_path = re.match(u".*{}/(.*{})".format(
                    formatted_path, item["name"]), item["path"]).group(1)
            # otherwise give everything after the first /~/ or /
            else:
                relative_path = re.match(u"(/~)*/(.*{})".format(
                    item["name"]), item["path"]).group(2)

            return relative_path + final_slash
        else:
            return item["name"] + final_slash

    # and then print it, per formatting rules
    formatted_print(
        res, fields=[('Permissions', 'permissions'), ('User', 'user'),
                     ('Group', 'group'), ('Size', 'size'),
                     ('Last Modified', 'last_modified'), ('File Type', 'type'),
                     ('Filename', formated_item_name)],
        simple_text=(None if long or is_verbose() or outformat_is_json() else
                     "\n".join(formated_item_name(x) for x in res)),
        json_converter=iterable_response_to_dict)
