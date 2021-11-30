"""
Internal types for type annotations
"""
from typing import TYPE_CHECKING, Callable, List, Tuple, Union

# all imports from globus_cli modules done here are done under TYPE_CHECKING
# in order to ensure that the use of type annotations never introduces circular
# imports at runtime
if TYPE_CHECKING:
    from globus_cli.termio import FormatField


FIELD_T = Union[
    "FormatField",
    Tuple[str, str],
    Tuple[str, Callable[..., str]],
]

FIELD_LIST_T = List[FIELD_T]
