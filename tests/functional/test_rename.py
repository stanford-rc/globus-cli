def test_simple_rename_success(run_line, load_api_fixtures, go_ep1_id):
    """
    Just confirm that args make it through the command successfully and we render the
    message as output.
    """
    load_api_fixtures("transfer_activate_success.yaml")
    load_api_fixtures("rename_result.yaml")

    result = run_line(f"globus rename {go_ep1_id} foo/bar /baz/buzz")
    assert "File or directory renamed successfully" in result.output
