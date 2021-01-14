import json

from tests.constants import GO_EP1_ID


def test_bookmark_create(run_line, load_api_fixtures):
    """
    Runs bookmark create, confirms simple things about text and json output
    """
    data = load_api_fixtures("bookmark_operations.yaml")
    bookmark_id = data["metadata"]["bookmark_id"]
    result = run_line("globus bookmark create {}:/share/ sharebm".format(GO_EP1_ID))
    assert "Bookmark ID: {}".format(bookmark_id) in result.output

    # repeat, but with JSON output
    json_output = json.loads(
        run_line(
            "globus bookmark create -Fjson {}:/share/ sharebm".format(GO_EP1_ID)
        ).output
    )
    assert json_output["id"] == bookmark_id
    assert json_output["name"] == "sharebm"
    assert json_output["path"] == "/share/"
    assert json_output["endpoint_id"] == GO_EP1_ID


def test_bookmark_show(run_line, load_api_fixtures):
    """
    Runs bookmark show on bm1's name and id.
    Confirms both inputs work, and verbose output is as expected.
    """
    data = load_api_fixtures("bookmark_operations.yaml")
    bookmark_id = data["metadata"]["bookmark_id"]
    bookmark_name = data["metadata"]["bookmark_name"]

    # id
    result = run_line('globus bookmark show "{}"'.format(bookmark_id))
    assert "{}:/share/\n".format(GO_EP1_ID) == result.output

    # name
    result = run_line('globus bookmark show "{}"'.format(bookmark_name))
    assert "{}:/share/\n".format(GO_EP1_ID) == result.output

    # verbose
    result = run_line("globus bookmark show -v {}".format(bookmark_id))
    assert "Endpoint ID: {}".format(GO_EP1_ID) in result.output


def test_bookmark_rename_by_id(run_line, load_api_fixtures):
    """
    Runs bookmark rename on bm1's id.
    """
    data = load_api_fixtures("bookmark_operations.yaml")
    bookmark_id = data["metadata"]["bookmark_id"]
    updated_bookmark_name = data["metadata"]["bookmark_name_after_update"]

    result = run_line(
        'globus bookmark rename "{}" "{}"'.format(bookmark_id, updated_bookmark_name)
    )
    assert "Success" in result.output


def test_bookmark_rename_by_name(run_line, load_api_fixtures):
    """
    Runs bookmark rename on bm1's name. Confirms can be shown by new name.
    """
    data = load_api_fixtures("bookmark_operations.yaml")
    bookmark_name = data["metadata"]["bookmark_name"]
    updated_bookmark_name = data["metadata"]["bookmark_name_after_update"]

    result = run_line(
        'globus bookmark rename "{}" "{}"'.format(bookmark_name, updated_bookmark_name)
    )
    assert "Success" in result.output


def test_bookmark_delete_by_id(run_line, load_api_fixtures):
    """
    Runs bookmark delete on bm1's id. Confirms success message.
    """
    data = load_api_fixtures("bookmark_operations.yaml")
    bookmark_id = data["metadata"]["bookmark_id"]
    result = run_line('globus bookmark delete "{}"'.format(bookmark_id))
    assert "deleted successfully" in result.output


def test_bookmark_delete_by_name(run_line, load_api_fixtures):
    """
    Runs bookmark delete on bm1's name. Confirms success message.
    """
    data = load_api_fixtures("bookmark_operations.yaml")
    bookmark_name = data["metadata"]["bookmark_name"]
    result = run_line('globus bookmark delete "{}"'.format(bookmark_name))
    assert "deleted successfully" in result.output
