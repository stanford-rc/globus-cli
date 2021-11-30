import functools
import uuid
from typing import Dict, Iterator, List, Optional, Tuple

import click
import globus_sdk
from globus_sdk.scopes import AuthScopes, GroupsScopes, SearchScopes, TransferScopes

from globus_cli.endpointish import Endpointish, EndpointType

from .. import version
from ..services.auth import CustomAuthClient
from ..services.gcs import CustomGCSClient
from ..services.transfer import CustomTransferClient
from .auth_flows import do_link_auth_flow, do_local_server_auth_flow
from .errors import MissingLoginError
from .local_server import is_remote_session
from .tokenstore import internal_auth_client, token_storage_adapter


class LoginManager:
    # TEST_MODE skips token validation
    _TEST_MODE: bool = False

    AUTH_RS = AuthScopes.resource_server
    TRANSFER_RS = TransferScopes.resource_server
    GROUPS_RS = GroupsScopes.resource_server
    SEARCH_RS = SearchScopes.resource_server

    STATIC_SCOPES: Dict[str, List[str]] = {
        AUTH_RS: [
            AuthScopes.openid,
            AuthScopes.profile,
            AuthScopes.email,
            AuthScopes.view_identity_set,
        ],
        TRANSFER_RS: [
            TransferScopes.all,
        ],
        GROUPS_RS: [
            GroupsScopes.all,
        ],
        SEARCH_RS: [
            SearchScopes.all,
        ],
    }

    def __init__(self) -> None:
        self._token_storage = token_storage_adapter()
        self._nonstatic_requirements: Dict[str, List[str]] = {}

    def add_requirement(self, rs_name: str, scopes: List[str]) -> None:
        self._nonstatic_requirements[rs_name] = scopes

    @property
    def login_requirements(self) -> Iterator[Tuple[str, List[str]]]:
        yield from self.STATIC_SCOPES.items()
        yield from self._nonstatic_requirements.items()

    @property
    def always_required_scopes(self) -> Iterator[str]:
        """
        scopes which are required on all login flows, regardless of the specified
        scopes for that flow
        """
        # openid -> required to ensure the presence of an id_token in the response data
        # WARNING:
        # all other Auth scopes are required the moment we add 'openid'
        # adding 'openid' without other scopes gives us back an Auth token which is not
        # valid for the other necessary scopes
        yield from self.STATIC_SCOPES[self.AUTH_RS]

    def is_logged_in(self) -> bool:
        res = []
        for rs_name, _scopes in self.login_requirements:
            res.append(self.has_login(rs_name))
        return all(res)

    def _validate_token(self, token: str) -> bool:
        if self._TEST_MODE:
            return True

        auth_client = internal_auth_client()
        try:
            res = auth_client.oauth2_validate_token(token)
        # if the instance client is invalid, an AuthAPIError will be raised
        except globus_sdk.AuthAPIError:
            return False
        return bool(res["active"])

    def has_login(self, resource_server: str) -> bool:
        """
        Determines if the user has a valid refresh token for the given
        resource server
        """
        tokens = self._token_storage.get_token_data(resource_server)
        if tokens is None or "refresh_token" not in tokens:
            return False
        rt = tokens["refresh_token"]
        return self._validate_token(rt)

    def run_login_flow(
        self,
        *,
        no_local_server: bool = False,
        local_server_message: Optional[str] = None,
        epilog: Optional[str] = None,
        session_params: Optional[dict] = None,
        scopes: Optional[List[str]] = None,
    ):
        if scopes is None:  # flatten scopes to list of strings if none provided
            scopes = [
                s for _rs_name, rs_scopes in self.login_requirements for s in rs_scopes
            ]
        # ensure that the requested scope list contains the scopes which are listed as
        # "always required"
        for s in self.always_required_scopes:
            if s not in scopes:
                scopes.append(s)
        # use a link login if remote session or user requested
        if no_local_server or is_remote_session():
            do_link_auth_flow(scopes, session_params=session_params)
        # otherwise default to a local server login flow
        else:
            if local_server_message is not None:
                click.echo(local_server_message)
            do_local_server_auth_flow(scopes, session_params=session_params)

        if epilog is not None:
            click.echo(epilog)

    def assert_logins(self, *resource_servers, assume_gcs=False):
        # determine the set of resource servers missing logins
        missing_servers = {s for s in resource_servers if not self.has_login(s)}

        # if we are missing logins, assemble error text
        # text is slightly different for 1, 2, or 3+ missing servers
        if missing_servers:
            raise MissingLoginError(missing_servers, assume_gcs=assume_gcs)

    @classmethod
    def requires_login(cls, *resource_servers: str):
        """
        Command decorator for specifying a resource server that the user must have
        tokens for in order to run the command.

        Simple usage for commands that have static resource needs: simply list all
        needed resource servers as args:

        @LoginManager.requries_login("auth.globus.org")

        @LoginManager.requries_login(LoginManager.AUTH_RS)

        @LoginManager.requires_login("auth.globus.org", "transfer.api.globus.org")

        @LoginManager.requries_login(LoginManager.AUTH_RS, LoginManager.TRANSFER_RS)

        Usage for commands which have dynamic resource servers depending
        on the arguments passed to the command (e.g. commands for the GCS API)

        @LoginManager.requies_login()
        def command(login_manager, endpoint_id)

            login_manager.<do the thing>(endpoint_id)

        """

        def inner(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                manager = cls()
                manager.assert_logins(*resource_servers)
                return func(*args, login_manager=manager, **kwargs)

            return wrapper

        return inner

    def _get_client_authorizer(
        self, resource_server: str, *, no_tokens_msg: Optional[str] = None
    ) -> globus_sdk.RefreshTokenAuthorizer:
        tokens = self._token_storage.get_token_data(resource_server)

        # if there are no tokens, raise an error
        # this *should* never be reached, but it's a safety check to ensure we never go
        # into a bad state
        if tokens is None:
            raise ValueError(
                no_tokens_msg
                or f"Could not get login data for {resource_server}. Try login to fix."
            )

        return globus_sdk.RefreshTokenAuthorizer(
            tokens["refresh_token"],
            internal_auth_client(),
            access_token=tokens["access_token"],
            expires_at=tokens["expires_at_seconds"],
            on_refresh=self._token_storage.on_refresh,
        )

    def get_transfer_client(self) -> CustomTransferClient:
        authorizer = self._get_client_authorizer(TransferScopes.resource_server)
        return CustomTransferClient(authorizer=authorizer, app_name=version.app_name)

    def get_auth_client(self) -> CustomAuthClient:
        authorizer = self._get_client_authorizer(AuthScopes.resource_server)
        return CustomAuthClient(authorizer=authorizer, app_name=version.app_name)

    def get_groups_client(self) -> globus_sdk.GroupsClient:
        authorizer = self._get_client_authorizer(GroupsScopes.resource_server)
        return globus_sdk.GroupsClient(authorizer=authorizer, app_name=version.app_name)

    def get_search_client(self) -> globus_sdk.SearchClient:
        authorizer = self._get_client_authorizer(SearchScopes.resource_server)
        return globus_sdk.SearchClient(authorizer=authorizer, app_name=version.app_name)

    def _get_gcs_info(
        self,
        *,
        collection_id: Optional[uuid.UUID] = None,
        endpoint_id: Optional[uuid.UUID] = None,
    ) -> Tuple[str, Endpointish]:
        if collection_id is not None and endpoint_id is not None:  # pragma: no cover
            raise ValueError("Internal Error! collection_id and endpoint_id are mutex")

        transfer_client = self.get_transfer_client()

        if collection_id is not None:
            epish = Endpointish(collection_id, transfer_client=transfer_client)
            resolved_ep_id = epish.get_collection_endpoint_id()
        elif endpoint_id is not None:
            epish = Endpointish(endpoint_id, transfer_client=transfer_client)
            epish.assert_ep_type(EndpointType.GCSV5_ENDPOINT)
            resolved_ep_id = str(endpoint_id)
        else:  # pragma: no cover
            raise ValueError("Internal Error! collection_id or endpoint_id is required")
        return (resolved_ep_id, epish)

    def get_gcs_client(
        self,
        *,
        collection_id: Optional[uuid.UUID] = None,
        endpoint_id: Optional[uuid.UUID] = None,
    ) -> CustomGCSClient:
        gcs_id, epish = self._get_gcs_info(
            collection_id=collection_id, endpoint_id=endpoint_id
        )

        self.assert_logins(gcs_id, assume_gcs=True)

        authorizer = self._get_client_authorizer(
            gcs_id,
            no_tokens_msg=(
                f"Could not get login data for GCS {gcs_id}. "
                f"Try login with '--gcs {gcs_id}' to fix."
            ),
        )
        return CustomGCSClient(
            epish.get_gcs_address(),
            source_epish=epish,
            authorizer=authorizer,
            app_name=version.app_name,
        )
