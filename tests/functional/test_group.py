import json

import responses
from globus_sdk._testing import load_response_set


def test_group_list(run_line):
    """
    Runs globus group list and validates results
    """
    meta = load_response_set("cli.groups").metadata

    group1_id = meta["group1_id"]
    group2_id = meta["group2_id"]
    group1_name = meta["group1_name"]
    group2_name = meta["group2_name"]

    result = run_line("globus group list")

    assert group1_id in result.output
    assert group2_id in result.output
    assert group1_name in result.output
    assert group2_name in result.output


def test_group_show(run_line):
    """
    Basic success test for globus group show
    """
    meta = load_response_set("cli.groups").metadata

    group1_id = meta["group1_id"]
    group1_name = meta["group1_name"]
    group1_description = meta["group1_description"]

    result = run_line(f"globus group show {group1_id}")

    assert group1_name in result.output
    assert group1_description in result.output


def test_group_create(run_line):
    """
    Basic success test for globus group create
    """
    meta = load_response_set("cli.groups").metadata

    group1_id = meta["group1_id"]
    group1_name = meta["group1_name"]
    group1_description = meta["group1_description"]

    result = run_line(
        f"globus group create '{group1_name}' --description '{group1_description}'"
    )

    assert f"Group {group1_id} created successfully" in result.output


def test_group_update(run_line):
    """
    Basic success test for globus group update
    Confirms existing values are included in the put document when
    not specified by options
    """
    meta = load_response_set("cli.groups").metadata

    group1_id = meta["group1_id"]
    group1_name = meta["group1_name"]
    group1_description = meta["group1_description"]
    new_name = "New Name"
    new_description = "New Description"

    # update name
    result = run_line(f"globus group update {group1_id} --name '{new_name}'")
    assert "Group updated successfully" in result.output

    # confirm description is in the put document with the pre-existing value
    last_req = responses.calls[-1].request
    sent = json.loads(last_req.body)
    assert sent["name"] == new_name
    assert sent["description"] == group1_description

    # update description
    result = run_line(
        f"globus group update {group1_id} --description '{new_description}'"
    )
    assert "Group updated successfully" in result.output

    # confirm name is in the put document with the pre-existing value
    last_req = responses.calls[-1].request
    sent = json.loads(last_req.body)
    assert sent["name"] == group1_name
    assert sent["description"] == new_description

    # update both name and description
    result = run_line(
        f"globus group update {group1_id} "
        f"--name '{new_name}' --description '{new_description}'"
    )
    assert "Group updated successfully" in result.output

    # confirm both fields use new value
    last_req = responses.calls[-1].request
    sent = json.loads(last_req.body)
    assert sent["name"] == new_name
    assert sent["description"] == new_description


def test_group_delete(run_line):
    """
    Basic success test for globus group delete
    """
    meta = load_response_set("cli.groups").metadata

    group1_id = meta["group1_id"]

    result = run_line(f"globus group delete {group1_id}")

    assert "Group deleted successfully" in result.output


def test_group_member_add(run_line):
    meta = load_response_set("cli.groups").metadata
    group = meta["group1_id"]
    member = meta["user1_id"]
    result = run_line(f"globus group member add {group} {member}")
    username = meta["user1_username"]
    assert member in result.output
    assert username in result.output
    assert group in result.output
    sent_data = json.loads(responses.calls[-1].request.body)
    assert "add" in sent_data
    assert len(sent_data["add"]) == 1
    assert sent_data["add"][0]["identity_id"] == member


def test_group_member_add_failure(run_line):
    meta = load_response_set("cli.groups").metadata
    group = meta["group1_id"]
    bad_identity = "NOT_A_VALID_USER"
    result = run_line(
        f"globus group member add {group} {bad_identity}", assert_exit_code=2
    )
    assert "Error" in result.stderr
    assert bad_identity in result.stderr


def test_group_member_add_already_in_group(run_line):
    meta = load_response_set("cli.groups").metadata
    group = meta["group_already_added_user_id"]
    member = meta["user1_id"]
    result = run_line(f"globus group member add {group} {member}", assert_exit_code=1)
    assert "already an active member of the group" in result.stderr


def test_group_member_remove(run_line):
    meta = load_response_set("cli.groups").metadata
    group = meta["group_remove_id"]
    member = meta["user1_id"]
    username = meta["user1_username"]
    result = run_line(f"globus group member remove {group} {member}")
    assert member in result.output
    assert username in result.output
    assert group in result.output
    sent_data = json.loads(responses.calls[-1].request.body)
    assert "remove" in sent_data
    assert len(sent_data["remove"]) == 1
    assert sent_data["remove"][0]["identity_id"] == member


def test_group_member_already_removed(run_line):
    meta = load_response_set("cli.groups").metadata
    group = meta["group_user_remove_error"]
    member = meta["user1_id"]
    result = run_line(
        f"globus group member remove {group} {member}", assert_exit_code=1
    )
    assert "Identity has no membership in group" in result.stderr
