def test_path(run_line, load_api_fixtures, go_ep1_id):
    """
    Does an ls on EP1:/, confirms expected results.
    """
    load_api_fixtures("transfer_activate_success.yaml")
    load_api_fixtures("ls_results.yaml")
    result = run_line(f"globus ls {go_ep1_id}:/")

    expected = ["home/", "mnt/", "not shareable/", "share/"]
    for item in expected:
        assert item in result.output


def test_recursive(run_line, load_api_fixtures, go_ep1_id):
    """
    Confirms --recursive ls on EP1:/share/ finds file1.txt
    """
    load_api_fixtures("transfer_activate_success.yaml")
    load_api_fixtures("ls_results.yaml")
    result = run_line(f"globus ls -r {go_ep1_id}:/share")
    assert "file1.txt" in result.output


# regression test for
#   https://github.com/globus/globus-cli/issues/577
def test_recursive_empty(run_line, load_api_fixtures, go_ep1_id):
    """
    empty recursive ls should have an empty result
    """
    load_api_fixtures("transfer_activate_success.yaml")
    load_api_fixtures("ls_results.yaml")
    result = run_line(f"globus ls -r {go_ep1_id}:/mnt")
    assert result.output.strip() == ""


def test_depth(run_line, load_api_fixtures, go_ep1_id):
    """
    Confirms setting depth to 1 on a --recursive ls of EP1:/
    finds godata but not file1.txt
    """
    load_api_fixtures("transfer_activate_success.yaml")
    load_api_fixtures("ls_results.yaml")
    result = run_line(f"globus ls -r --recursive-depth-limit 1 {go_ep1_id}:/")
    assert "file1.txt" not in result.output


def test_recursive_json(run_line, load_api_fixtures, go_ep1_id):
    """
    Confirms -F json works with the RecursiveLsResponse
    """
    load_api_fixtures("transfer_activate_success.yaml")
    load_api_fixtures("ls_results.yaml")
    result = run_line(f"globus ls -r -F json {go_ep1_id}:/share")
    assert '"DATA":' in result.output
    assert '"name": "godata/file1.txt"' in result.output
