import pytest


def test_guest_collection_delete(run_line, load_api_fixtures, add_gcs_login):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]
    cid = data["metadata"]["guest_collection_id"]
    add_gcs_login(epid)

    result = run_line(f"globus collection delete {cid}")
    assert "success" in result.output


def test_mapped_collection_delete(run_line, load_api_fixtures, add_gcs_login):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]
    cid = data["metadata"]["mapped_collection_id"]
    add_gcs_login(epid)

    result = run_line(f"globus collection delete {cid}")
    assert "success" in result.output


def test_collection_delete_missing_login(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]
    cid = data["metadata"]["guest_collection_id"]

    result = run_line(f"globus collection delete {cid}", assert_exit_code=1)
    assert "success" not in result.output
    assert f"Missing login for {epid}" in result.stderr
    assert f"  globus login --gcs {epid}" in result.stderr


def test_collection_delete_on_gcsv5_host(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]

    result = run_line(f"globus collection delete {epid}", assert_exit_code=2)
    assert "success" not in result.output
    assert (
        f"Expected {epid} to be a collection ID.\n"
        "Instead, found it was of type 'Globus Connect Server v5 Endpoint'."
    ) in result.stderr
    assert "This operation is not supported on objects of this type." in result.stderr


def test_collection_delete_on_gcp(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["gcp_endpoint_id"]

    result = run_line(f"globus collection delete {epid}", assert_exit_code=2)
    assert "success" not in result.output
    assert (
        f"Expected {epid} to be a collection ID.\n"
        "Instead, found it was of type 'Globus Connect Personal'."
    ) in result.stderr
    assert (
        "Please run the following command instead:\n\n"
        f"    globus endpoint delete {epid}"
    ) in result.stderr


def test_collection_show(run_line, load_api_fixtures, add_gcs_login):
    data = load_api_fixtures("collection_operations.yaml")
    cid = data["metadata"]["mapped_collection_id"]
    username = data["metadata"]["username"]
    epid = data["metadata"]["endpoint_id"]
    add_gcs_login(epid)

    _result, matcher = run_line(f"globus collection show {cid}", matcher=True)

    matcher.check(r"^Display Name:\s+(.*)$", groups=["Happy Fun Collection Name"])
    matcher.check(r"^Owner:\s+(.*)$", groups=[username])
    matcher.check(r"^ID:\s+(.*)$", groups=[cid])
    matcher.check(r"^Collection Type:\s+(.*)$", groups=["mapped"])
    matcher.check(r"^Connector:\s+(.*)$", groups=["POSIX"])


def test_collection_show_private_policies(run_line, load_api_fixtures, add_gcs_login):
    data = load_api_fixtures("collection_show_private_policies.yaml")
    cid = data["metadata"]["collection_id"]
    username = data["metadata"]["username"]
    epid = data["metadata"]["endpoint_id"]
    add_gcs_login(epid)

    _result, matcher = run_line(
        f"globus collection show --include-private-policies {cid}", matcher=True
    )

    matcher.check(r"^Display Name:\s+(.*)$", groups=["Happy Fun Collection Name"])
    matcher.check(r"^Owner:\s+(.*)$", groups=[username])
    matcher.check(r"^ID:\s+(.*)$", groups=[cid])
    matcher.check(r"^Collection Type:\s+(.*)$", groups=["mapped"])
    matcher.check(r"^Connector:\s+(.*)$", groups=["POSIX"])

    matcher.check(r"Root Path:\s+(.*)$", groups=["/"])
    matcher.check(
        r"^Sharing Path Restrictions:\s+(.*)$",
        groups=[
            '{"DATA_TYPE": "path_restrictions#1.0.0", "none": ["/"], "read": ["/projects"], "read_write": ["$HOME"]}',  # noqa: E501
        ],
    )


@pytest.mark.parametrize(
    "epid_key, ep_type",
    [
        ("gcp_endpoint_id", "Globus Connect Personal"),
        ("endpoint_id", "Globus Connect Server v5 Endpoint"),
    ],
)
def test_collection_show_on_non_collection(
    run_line, load_api_fixtures, epid_key, ep_type
):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"][epid_key]

    result = run_line(f"globus collection show {epid}", assert_exit_code=2)
    assert (
        f"Expected {epid} to be a collection ID.\n"
        f"Instead, found it was of type '{ep_type}'."
    ) in result.stderr
    assert (
        "Please run the following command instead:\n\n"
        f"    globus endpoint show {epid}"
    ) in result.stderr
