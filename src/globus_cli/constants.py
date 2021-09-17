"""
This module is used to define constants used throughout the code.
It should not depend on any other part of the globus-cli codebase.

(If you need to import something else, maybe it's not simple enough to be a constant...)
"""

__all__ = ["EXPLICIT_NULL"]


# this object is a sentinel value used to disambiguate values which are being
# intentionally nulled from values which are incidentally `None` because no
# argument was provided
EXPLICIT_NULL = object()
