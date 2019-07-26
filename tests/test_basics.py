import json

from tests.framework.constants import GO_EP1_ID, GO_EP2_ID
from tests.framework.tools import on_windows

# TODO: remove this as part of handling #455
PATHSEP = "\\" if on_windows() else "/"


def test_parsing(run_line):
    """
    Runs --help and confirms the option is parsed
    """
    # globus --help
    result = run_line("globus --help")
    assert "-h, --help" in result.output
    assert "Show this message and exit." in result.output


def test_command(run_line):
    """
    Runs list-commands and confirms the command is run
    """
    result = run_line("globus list-commands")
    assert "=== globus ===" in result.output


def test_command_parsing(run_line):
    """
    Runs list-commands --help
    confirms both the command and the option are parsed
    """
    result = run_line("globus list-commands --help")
    assert "List all Globus CLI Commands with short help output." in result.output


def test_command_missing_args(run_line):
    """
    Runs get-identities without values, confirms exit_code 2
    """
    result = run_line("globus get-identities", assert_exit_code=2)
    assert "Error: Missing argument" in result.output


def test_invalid_command(run_line):
    """
    Runs globus invalid-command, confirms Error
    """
    result = run_line("globus invalid-command", assert_exit_code=2)
    assert "Error: No such command" in result.output


def test_whoami(run_line, user_data):
    """
    Runs whoami to confirm test config successfully setup
    """
    result = run_line("globus whoami")
    assert user_data["clitester1a"]["username"] in result.output


def test_whoami_no_auth(run_line):
    """
    Runs whoami with config set to be empty, confirms no login seen.
    """
    result = run_line("globus whoami", config={}, assert_exit_code=1)
    assert "Unable to get user information" in result.output


def test_json_raw_string_output(run_line, user_data):
    """
    Get single-field jmespath output and make sure it's quoted
    """
    result = run_line("globus whoami --jmespath name")
    assert '"{}"'.format(user_data["clitester1a"]["name"]) == result.output.strip()


def test_auth_call_no_auth(run_line, user_data):
    """
    Runs get-identities with config set to be empty,
    confirms No Authentication CLI error.
    """
    result = run_line(
        "globus get-identities " + user_data["clitester1a"]["username"],
        config={},
        assert_exit_code=1,
    )
    assert "No Authentication provided." in result.output


def test_auth_call(run_line, user_data):
    """
    Runs get-identities using test auth refresh token to confirm
    test auth refresh token is live and configured correctly
    """
    result = run_line("globus get-identities " + user_data["clitester1a"]["username"])
    assert user_data["clitester1a"]["id"] in result.output


def test_transfer_call_no_auth(run_line):
    """
    Runs ls with config set to be empty,
    confirms No Authentication CLI error.
    """
    result = run_line("globus ls " + str(GO_EP1_ID), config={}, assert_exit_code=1)
    assert "No Authentication provided." in result.output


def test_transfer_call(run_line):
    """
    Runs ls using test transfer refresh token to confirm
    test transfer refresh token is live and configured correctly
    """
    result = run_line("globus ls " + str(GO_EP1_ID) + ":/")
    assert "home/" in result.output


def test_transfer_batchmode_dryrun(run_line):
    """
    Dry-runs a transfer in batchmode, confirms batchmode inputs received
    """
    batch_input = u"abc /def\n/xyz p/q/r\n"
    result = run_line(
        "globus transfer -F json --batch --dry-run "
        + str(GO_EP1_ID)
        + " "
        + str(GO_EP2_ID),
        stdin=batch_input,
    )
    # rely on json.dumps() in order to get the quoting right in the Windows
    # case
    # FIXME: this should be removed after we resolve #455
    for src, dst in [
        ("abc", "{}def".format(PATHSEP)),
        ("{}xyz".format(PATHSEP), "p{sep}q{sep}r".format(sep=PATHSEP)),
    ]:
        assert '"source_path": {}'.format(json.dumps(src)) in result.output
        assert '"destination_path": {}'.format(json.dumps(dst)) in result.output


def test_delete_batchmode_dryrun(run_line):
    """
    Dry-runs a delete in batchmode
    """
    batch_input = u"abc/def\n/xyz\n"
    result = run_line(
        "globus delete --batch --dry-run " + str(GO_EP1_ID), stdin=batch_input
    )
    assert ("\n".join(("Path   ", "-------", "abc{sep}def", "{sep}xyz   \n"))).format(
        sep=PATHSEP
    ) == result.output
