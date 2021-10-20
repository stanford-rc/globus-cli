import logging
import sys
import textwrap
import uuid
from typing import Any, Dict, Tuple, Union

import click
from globus_sdk import GlobusHTTPResponse, RefreshTokenAuthorizer, TransferClient

from globus_cli import login_manager, version
from globus_cli.termio import FORMAT_SILENT, formatted_print

from .data import display_name_or_cname
from .recursive_ls import RecursiveLsResponse

log = logging.getLogger(__name__)


class CustomTransferClient(TransferClient):
    # TDOD: Remove this function when endpoints natively support recursive ls
    def recursive_operation_ls(
        self,
        endpoint_id: Union[str, uuid.UUID],
        params: Dict[str, Any],
        depth: int = 3,
    ) -> RecursiveLsResponse:
        """
        Makes recursive calls to ``GET /operation/endpoint/<endpoint_id>/ls``
        Does not preserve access to top level operation_ls fields, but
        adds a "path" field for every item that represents the full
        path to that item.

        :rtype: iterable of :class:`GlobusResponse <globus_sdk.response.GlobusResponse>`

        :param endpoint_id: The endpoint being recursively ls'ed. If no "path" is given
            in params, the start path is determined by this endpoint.
        :param params: Parameters that will be passed through as query params.
        :param depth: The maximum file depth the recursive ls will go to.
        """
        endpoint_id = str(endpoint_id)
        log.info(
            "TransferClient.recursive_operation_ls(%s, %s, %s)",
            endpoint_id,
            depth,
            params,
        )
        return RecursiveLsResponse(self, endpoint_id, params, max_depth=depth)

    def get_endpoint_w_server_list(
        self, endpoint_id
    ) -> Tuple[GlobusHTTPResponse, Union[str, GlobusHTTPResponse]]:
        """
        A helper for handling endpoint server list lookups correctly accounting
        for various endpoint types.

        - Raises click.UsageError when used on Shares
        - Returns (<get_endpoint_response>, "S3") for S3 endpoints
        - Returns (<get_endpoint_response>, <server_list_response>) for all other
          Endpoints
        """
        endpoint = self.get_endpoint(endpoint_id)

        if endpoint["host_endpoint_id"]:  # not GCS -- this is a share endpoint
            raise click.UsageError(
                textwrap.dedent(
                    """\
                {id} ({0}) is a share and does not have servers.

                To see details of the share, use
                    globus endpoint show {id}

                To list the servers on the share's host endpoint, use
                    globus endpoint server list {host_endpoint_id}
            """
                ).format(display_name_or_cname(endpoint), **endpoint.data)
            )

        if endpoint["s3_url"]:  # not GCS -- legacy S3 endpoint type
            return (endpoint, "S3")

        else:
            return (endpoint, self.endpoint_server_list(endpoint_id))

    def task_wait_with_io(
        self, meow, heartbeat, polling_interval, timeout, task_id, timeout_exit_code
    ) -> None:
        """
        Options are the core "task wait" options, including the `--meow` easter
        egg.

        This does the core "task wait" loop, including all of the IO.
        It *does exit* on behalf of the caller. (We can enhance with a
        `noabort=True` param or somesuch in the future if necessary.)
        """

        def timed_out(waited_time):
            if timeout is None:
                return False
            else:
                return waited_time >= timeout

        def check_completed():
            completed = self.task_wait(
                task_id, timeout=polling_interval, polling_interval=polling_interval
            )
            if completed:
                if heartbeat:
                    click.echo("", err=True)
                # meowing tasks wake up!
                if meow:
                    click.echo(
                        r"""
                      _..
      /}_{\           /.-'
     ( a a )-.___...-'/
     ==._.==         ;
          \ i _..._ /,
          {_;/   {_//""",
                        err=True,
                    )

                # TODO: possibly update TransferClient.task_wait so that we don't
                # need to do an extra fetch to get the task status after completion
                res = self.get_task(task_id)
                formatted_print(res, text_format=FORMAT_SILENT)

                status = res["status"]
                if status == "SUCCEEDED":
                    click.get_current_context().exit(0)
                else:
                    click.get_current_context().exit(1)

            return completed

        # Tasks start out sleepy
        if meow:
            click.echo(
                r"""
       |\      _,,,---,,_
       /,`.-'`'    -.  ;-;;,_
      |,4-  ) )-,_..;\ (  `'-'
     '---''(_/--'  `-'\_)""",
                err=True,
            )

        waited_time = 0
        while not timed_out(waited_time) and not check_completed():
            if heartbeat:
                click.echo(".", err=True, nl=False)
                sys.stderr.flush()

            waited_time += polling_interval

        # add a trailing newline to heartbeats if we fail
        if heartbeat:
            click.echo("", err=True)

        exit_code = 1
        if timed_out(waited_time):
            click.echo(f"Task has yet to complete after {timeout} seconds", err=True)
            exit_code = timeout_exit_code

        # output json if requested, but nothing for text mode
        res = self.get_task(task_id)
        formatted_print(res, text_format=FORMAT_SILENT)

        click.get_current_context().exit(exit_code)


def get_client() -> CustomTransferClient:
    adapter = login_manager.token_storage_adapter()
    tokens = adapter.get_token_data("transfer.api.globus.org")
    authorizer = None

    # if there are tokens, build the authorizer
    if tokens is not None:
        authorizer = RefreshTokenAuthorizer(
            tokens["refresh_token"],
            login_manager.internal_auth_client(),
            access_token=tokens["access_token"],
            expires_at=tokens["expires_at_seconds"],
            on_refresh=adapter.on_refresh,
        )

    return CustomTransferClient(authorizer=authorizer, app_name=version.app_name)
