from typing import Iterable, Optional

from .endpoint_type import EndpointType

SHOULD_USE_MAP = {
    "globus collection delete": [
        ("globus endpoint delete", EndpointType.traditional_endpoints()),
    ],
    "globus endpoint delete": [
        ("globus collection delete", EndpointType.collections()),
    ],
}


class WrongEndpointTypeError(ValueError):
    def __init__(
        self,
        from_command: str,
        endpoint_id: str,
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
            for should_use, if_types in SHOULD_USE_MAP[self.from_command]:
                if self.actual_type in if_types:
                    return should_use
        return None


class ExpectedCollectionError(WrongEndpointTypeError):
    def expected_message(self):
        return f"Expected {self.endpoint_id} to be a collection ID."


class ExpectedEndpointError(WrongEndpointTypeError):
    def expected_message(self):
        return f"Expected {self.endpoint_id} to be an endpoint ID."
