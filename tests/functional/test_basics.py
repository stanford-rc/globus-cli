import uuid

from tests.constants import GO_EP1_ID, GO_EP2_ID


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


def test_whoami(run_line, register_api_route):
    """
    Runs whoami to confirm test config successfully setup
    """
    user_id = str(uuid.uuid4())
    register_api_route(
        "auth",
        "/v2/oauth2/userinfo",
        json={
            "preferred_username": "foo@globusid.org",
            "name": "Foo McUser",
            "sub": user_id,
            "email": "foo.mcuser@globus.org",
        },
    )

    result = run_line("globus whoami")
    assert result.output == "foo@globusid.org\n"


def test_whoami_no_auth(run_line, register_api_route):
    """
    Runs whoami with config set to be empty, confirms no login seen.
    """
    register_api_route(
        "auth",
        "/v2/oauth2/userinfo",
        status=401,
        json={"code": "UNAUTHORIZED", "message": "foo bar"},
    )
    result = run_line("globus whoami", config={}, assert_exit_code=1)
    assert "Unable to get user information" in result.output


def test_json_raw_string_output(run_line, register_api_route):
    """
    Get single-field jmespath output and make sure it's quoted
    """
    user_id = str(uuid.uuid4())
    register_api_route(
        "auth",
        "/v2/oauth2/userinfo",
        json={
            "preferred_username": "foo@globusid.org",
            "name": "Foo McUser",
            "sub": user_id,
            "email": "foo.mcuser@globus.org",
        },
    )
    result = run_line("globus whoami --jmespath name")
    assert '"Foo McUser"\n' == result.output


def test_auth_call_no_auth(run_line, register_api_route):
    """
    Runs get-identities with config set to be empty,
    confirms No Authentication CLI error.
    """
    register_api_route(
        "auth",
        "/v2/api/identities",
        status=401,
        json={"code": "UNAUTHORIZED", "message": "foo bar"},
    )
    result = run_line(
        "globus get-identities foo@globusid.org",
        config={},
        assert_exit_code=1,
    )
    assert "No Authentication provided." in result.output


def test_auth_call(run_line, register_api_route):
    """
    Runs get-identities using test auth refresh token to confirm
    test auth refresh token is live and configured correctly
    """
    user_id = str(uuid.uuid4())
    idp_id = str(uuid.uuid4())
    register_api_route(
        "auth",
        "/v2/api/identities",
        json={
            "identities": [
                {
                    "username": "foo@globusid.org",
                    "name": "Foo McUser",
                    "id": user_id,
                    "identity_provider": idp_id,
                    "organization": "McUser Group",
                    "status": "used",
                    "email": "foo.mcuser@globus.org",
                }
            ]
        },
    )
    result = run_line("globus get-identities foo@globusid.org")
    assert user_id in result.output


def test_transfer_call_no_auth(run_line, register_api_route):
    """
    Runs ls with config set to be empty,
    confirms No Authentication CLI error.
    """
    register_api_route(
        "transfer",
        "/endpoint/{}/autoactivate".format(GO_EP1_ID),
        method="POST",
        status=401,
        json={
            "code": "ClientError.AuthenticationFailed",
            "message": "foo bar",
            "request_id": "abc123",
        },
    )
    result = run_line("globus ls " + str(GO_EP1_ID), config={}, assert_exit_code=1)
    assert "No Authentication provided." in result.output


def test_transfer_call(run_line, register_api_route):
    """
    Runs ls using test transfer refresh token to confirm
    test transfer refresh token is live and configured correctly
    """
    register_api_route(
        "transfer",
        "/endpoint/{}/autoactivate".format(GO_EP1_ID),
        method="POST",
        # exact data doesn't matter, just not the failure code
        json={"code": "AutoActivated.BogusCode"},
    )
    register_api_route(
        "transfer",
        "/operation/endpoint/{}/ls".format(GO_EP1_ID),
        json={
            # not *quite* verbatim data from the API, but very similar and in the right
            # format with all fields populated
            "DATA": [
                {
                    "DATA_TYPE": "file",
                    "group": "root",
                    "last_modified": "2021-01-14 00:33:38+00:00",
                    "link_group": None,
                    "link_last_modified": None,
                    "link_size": None,
                    "link_target": None,
                    "link_user": None,
                    "name": name,
                    "permissions": "0755",
                    "size": 4096,
                    "type": "dir",
                    "user": "root",
                }
                for name in ["home", "mnt", "not shareable", "share"]
            ]
        },
    )
    result = run_line("globus ls " + str(GO_EP1_ID) + ":/")
    assert "home/" in result.output


def test_transfer_batchmode_dryrun(run_line, register_api_route):
    """
    Dry-runs a transfer in batchmode, confirms batchmode inputs received
    """
    # put a submission ID and autoactivate response in place
    submission_id = str(uuid.uuid4())
    register_api_route("transfer", "/submission_id", json={"value": submission_id})
    register_api_route(
        "transfer",
        "/endpoint/{}/autoactivate".format(GO_EP1_ID),
        method="POST",
        # exact data doesn't matter, just not the failure code
        json={"code": "AutoActivated.BogusCode"},
    )
    register_api_route(
        "transfer",
        "/endpoint/{}/autoactivate".format(GO_EP2_ID),
        method="POST",
        # exact data doesn't matter, just not the failure code
        json={"code": "AutoActivated.BogusCode"},
    )

    batch_input = u"abc /def\n/xyz p/q/r\n"
    result = run_line(
        "globus transfer -F json --batch --dry-run "
        + str(GO_EP1_ID)
        + " "
        + str(GO_EP2_ID),
        stdin=batch_input,
    )
    for src, dst in [("abc", "/def"), ("/xyz", "p/q/r")]:
        assert '"source_path": "{}"'.format(src) in result.output
        assert '"destination_path": "{}"'.format(dst) in result.output


def test_delete_batchmode_dryrun(run_line, register_api_route):
    """
    Dry-runs a delete in batchmode
    """
    # put a submission ID and autoactivate response in place
    submission_id = str(uuid.uuid4())
    register_api_route("transfer", "/submission_id", json={"value": submission_id})
    register_api_route(
        "transfer",
        "/endpoint/{}/autoactivate".format(GO_EP1_ID),
        method="POST",
        # exact data doesn't matter, just not the failure code
        json={"code": "AutoActivated.BogusCode"},
    )

    batch_input = u"abc/def\n/xyz\nabcdef\nabc/def/../xyz\n"
    result = run_line(
        "globus delete --batch --dry-run " + str(GO_EP1_ID), stdin=batch_input
    )
    assert (
        "\n".join(
            ("Path   ", "-------", "abc/def", "/xyz   ", "abcdef ", "abc/xyz", "")
        )
        == result.output
    )

    batch_input = u"abc/def\n/xyz\n../foo\n"
    result = run_line(
        "globus delete --batch --dry-run {}:foo/bar/./baz".format(GO_EP1_ID),
        stdin=batch_input,
    )
    assert (
        "\n".join(
            (
                "Path               ",
                "-------------------",
                "foo/bar/baz/abc/def",
                "/xyz               ",
                "foo/bar/foo        ",
                "",
            )
        )
        == result.output
    )
