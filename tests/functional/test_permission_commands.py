import json
import uuid

import pytest
import responses

DUMMY_ID1 = str(uuid.UUID(int=1))
DUMMY_ID2 = str(uuid.UUID(int=2))


@pytest.mark.parametrize("provision", [True, False])
def test_permission_create_identity_name(run_line, load_api_fixtures, provision):
    data = load_api_fixtures("endpoint_acl_operations.yaml")
    user_id = data["metadata"]["user_id"]
    username = data["metadata"]["username"]
    ep = data["metadata"]["endpoint_id"]

    result = run_line(
        [
            "globus",
            "endpoint",
            "permission",
            "create",
            f"{ep}:/",
            "--permissions",
            "rw",
            "--provision-identity" if provision else "--identity",
            username,
        ]
    )
    sent_data = json.loads(responses.calls[-1].request.body)
    assert sent_data["principal_type"] == "identity"
    assert sent_data["principal"] == user_id

    assert "Access rule created successfully." in result.stdout


def test_permission_create_identity_id(run_line, load_api_fixtures):
    data = load_api_fixtures("endpoint_acl_operations.yaml")
    user_id = data["metadata"]["user_id"]
    ep = data["metadata"]["endpoint_id"]

    result = run_line(
        [
            "globus",
            "endpoint",
            "permission",
            "create",
            f"{ep}:/",
            "--permissions",
            "rw",
            "--identity",
            user_id,
        ]
    )
    sent_data = json.loads(responses.calls[-1].request.body)
    assert sent_data["principal_type"] == "identity"
    assert sent_data["principal"] == user_id

    assert "Access rule created successfully." in result.stdout


def test_permission_create_requires_principal(run_line):
    dummy_ep = str(uuid.uuid1())
    result = run_line(
        [
            "globus",
            "endpoint",
            "permission",
            "create",
            f"{dummy_ep}:/",
            "--permissions",
            "rw",
        ],
        assert_exit_code=2,
    )
    assert "You must provide at least one principal" in result.stderr


@pytest.mark.parametrize(
    "addopts, expecterr",
    [
        (
            ["--identity", DUMMY_ID1, "--provision-identity", DUMMY_ID2],
            "Only one of --identity or --provision-identity allowed",
        ),
        (
            ["--identity", DUMMY_ID1, "--group", DUMMY_ID2],
            (
                "You have passed both an identity and a group. "
                "Please only pass one principal type"
            ),
        ),
        (
            ["--provision-identity", DUMMY_ID1, "--group", DUMMY_ID2],
            (
                "You have passed both an identity and a group. "
                "Please only pass one principal type"
            ),
        ),
        (
            ["--identity", DUMMY_ID1, "--anonymous"],
            "You may only pass one security principal",
        ),
        (
            ["--identity", DUMMY_ID1, "--all-authenticated"],
            "You may only pass one security principal",
        ),
    ],
)
def test_permission_create_incompatible_security_principal_opts(
    run_line, addopts, expecterr
):
    dummy_ep = str(uuid.uuid1())
    result = run_line(
        [
            "globus",
            "endpoint",
            "permission",
            "create",
            f"{dummy_ep}:/",
            "--permissions",
            "rw",
        ]
        + addopts,
        assert_exit_code=2,
    )
    assert expecterr in result.stderr


def test_permission_create_username_lookup_fails(run_line, register_api_route):
    register_api_route("auth", "/v2/api/identities", json={"identities": []})
    dummy_ep = str(uuid.uuid1())
    result = run_line(
        [
            "globus",
            "endpoint",
            "permission",
            "create",
            f"{dummy_ep}:/",
            "--permissions",
            "rw",
            "--identity",
            "foo@globus.org",
        ],
        assert_exit_code=2,
    )
    assert "Identity does not exist" in result.stderr
    assert "Use --provision-identity" in result.stderr
