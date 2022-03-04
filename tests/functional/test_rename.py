from globus_sdk._testing import load_response_set


def test_simple_rename_success(run_line, go_ep1_id):
    """
    Just confirm that args make it through the command successfully and we render the
    message as output.
    """
    load_response_set("cli.transfer_activate_success")
    load_response_set("cli.rename_result")

    result = run_line(f"globus rename {go_ep1_id} foo/bar /baz/buzz")
    assert "File or directory renamed successfully" in result.output
