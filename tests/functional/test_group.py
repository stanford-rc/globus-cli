import json

import responses


def test_group_list(run_line, load_api_fixtures):
    """
    Runs globus group list and validates results
    """
    data = load_api_fixtures("groups.yaml")

    group1_id = data["metadata"]["group1_id"]
    group2_id = data["metadata"]["group2_id"]
    group1_name = data["metadata"]["group1_name"]
    group2_name = data["metadata"]["group2_name"]

    result = run_line("globus group list")

    assert group1_id in result.output
    assert group2_id in result.output
    assert group1_name in result.output
    assert group2_name in result.output


def test_group_member_add(run_line, load_api_fixtures):
    data = load_api_fixtures("groups.yaml")
    group = data["metadata"]["group1_id"]
    member = data["metadata"]["user1_id"]
    result = run_line(f"globus group member add {group} {member}")
    username = data["metadata"]["user1_username"]
    assert member in result.output
    assert username in result.output
    assert group in result.output
    sent_data = json.loads(responses.calls[-1].request.body)
    assert "add" in sent_data
    assert len(sent_data["add"]) == 1
    assert sent_data["add"][0]["identity_id"] == member


def test_group_member_add_failure(run_line, load_api_fixtures):
    data = load_api_fixtures("groups.yaml")
    group = data["metadata"]["group1_id"]
    bad_identity = "NOT_A_VALID_USER"
    result = run_line(
        f"globus group member add {group} {bad_identity}", assert_exit_code=2
    )
    assert "Error" in result.stderr
    assert bad_identity in result.stderr


def test_group_member_add_already_in_group(run_line, load_api_fixtures):
    data = load_api_fixtures("groups.yaml")
    group = data["metadata"]["group_already_added_user_id"]
    member = data["metadata"]["user1_id"]
    result = run_line(f"globus group member add {group} {member}", assert_exit_code=1)
    assert "already an active member of the group" in result.stderr


def test_group_member_remove(run_line, load_api_fixtures):
    data = load_api_fixtures("groups.yaml")
    group = data["metadata"]["group_remove_id"]
    member = data["metadata"]["user1_id"]
    username = data["metadata"]["user1_username"]
    result = run_line(f"globus group member remove {group} {member}")
    assert member in result.output
    assert username in result.output
    assert group in result.output
    sent_data = json.loads(responses.calls[-1].request.body)
    assert "remove" in sent_data
    assert len(sent_data["remove"]) == 1
    assert sent_data["remove"][0]["identity_id"] == member
