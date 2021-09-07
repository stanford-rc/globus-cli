import os

import pytest

from globus_cli.termio import term_is_interactive


@pytest.mark.parametrize(
    "ps1, force_flag, expect",
    [
        (None, None, False),
        (None, "TRUE", True),
        (None, "0", False),
        ("$ ", None, True),
        ("$ ", "off", False),
        ("$ ", "on", True),
        ("$ ", "", True),
        ("", "", True),
        ("", None, True),
    ],
)
def test_term_interactive(ps1, force_flag, expect, monkeypatch):
    if ps1 is not None:
        monkeypatch.setitem(os.environ, "PS1", ps1)
    else:
        monkeypatch.delitem(os.environ, "PS1", raising=False)
    if force_flag is not None:
        monkeypatch.setitem(os.environ, "GLOBUS_CLI_INTERACTIVE", force_flag)
    else:
        monkeypatch.delitem(os.environ, "GLOBUS_CLI_INTERACTIVE", raising=False)

    assert term_is_interactive() == expect
