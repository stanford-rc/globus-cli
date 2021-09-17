"""
Endpointish, a dialect of Elvish spoken only within Globus.


The Endpointish is mostly an Endpoint document from the Transfer service, wrapped
with additional helpers and functionality.

Importantly, it is not meant to represent an Endpoint either in the sense of GCSv4 and
GCP nor in the sense of GCSv5. It represents a wrapped Endpoint document, with
introspection and other niceties.

Think of it as a TransferClient.get_endpoint call + a location to cache the result + any
decoration we might want for this.

The error types which can be produced if the type is not what is expected understand how
to "remap" commands from what was used to what should be used instead.
"""
import uuid
from typing import Iterable, Optional, Type, Union, cast

import click

from .services.transfer import EndpointType, get_client

SHOULD_USE_MAP = {
    "globus collection delete": (
        "globus endpoint delete",
        (EndpointType.GCP, EndpointType.SHARE, EndpointType.NON_GCSV5_ENDPOINT),
    )
}


class WrongEndpointTypeError(ValueError):
    def __init__(
        self,
        from_command: str,
        endpoint_id: Union[str, uuid.UUID],
        actual_type: EndpointType,
        expected_types: Iterable[EndpointType],
    ) -> None:
        self.from_command = from_command
        self.endpoint_id = str(endpoint_id)
        self.actual_type = actual_type
        self.expected_types = list(expected_types)
        self.messages = {
            "expect": self.expected_message(),
            "actual": self.actual_message(),
        }
        self.message_str = self.messages["expect"] + " " + self.messages["actual"]
        super().__init__(self.message_str)

    def expected_message(self) -> str:
        expect_str = ", ".join(EndpointType.nice_name(x) for x in self.expected_types)
        return f"Expected {self.endpoint_id} to be of type [{expect_str}]."

    def actual_message(self) -> str:
        actual_str = EndpointType.nice_name(self.actual_type)
        return f"Instead, found it was of type '{actual_str}'."

    def should_use_command(self) -> Optional[str]:
        if self.from_command in SHOULD_USE_MAP:
            should_use, if_types = SHOULD_USE_MAP[self.from_command]
            if self.actual_type in if_types:
                return should_use
        return None


class ExpectedCollectionError(WrongEndpointTypeError):
    def expected_message(self):
        return f"Expected {self.endpoint_id} to be a collection ID."


class Endpointish:
    def __init__(
        self,
        endpoint_id: Union[str, uuid.UUID],
    ):
        self._client = get_client()
        self.endpoint_id = endpoint_id

        res = self._client.get_endpoint(endpoint_id)
        self.data = res.data

        self.ep_type = EndpointType.determine_endpoint_type(self.data)

    def assert_ep_type(
        self,
        *expect_types: EndpointType,
        error_class: Type[WrongEndpointTypeError] = WrongEndpointTypeError,
    ):
        if self.ep_type not in expect_types:
            raise error_class(
                click.get_current_context().command_path,
                self.endpoint_id,
                self.ep_type,
                expect_types,
            )

    def assert_is_gcsv5_collection(self):
        self.assert_ep_type(
            EndpointType.GUEST_COLLECTION,
            EndpointType.MAPPED_COLLECTION,
            error_class=ExpectedCollectionError,
        )

    def get_collection_endpoint_id(self) -> str:
        self.assert_is_gcsv5_collection()
        return cast(str, self.data["owner_id"])
