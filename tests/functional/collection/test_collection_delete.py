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

    result = run_line(f"globus collection delete {cid}", assert_exit_code=4)
    assert "success" not in result.output
    assert f"Missing login for {epid}" in result.stderr
    assert f"  globus login --gcs {epid}" in result.stderr


def test_collection_delete_on_gcsv5_host(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]

    result = run_line(f"globus collection delete {epid}", assert_exit_code=3)
    assert "success" not in result.output
    assert (
        f"Expected {epid} to be a collection ID.\n"
        "Instead, found it was of type 'Globus Connect Server v5 Endpoint'."
    ) in result.stderr
    assert "This operation is not supported on objects of this type." in result.stderr


def test_collection_delete_on_gcp(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["gcp_endpoint_id"]

    result = run_line(f"globus collection delete {epid}", assert_exit_code=3)
    assert "success" not in result.output
    assert (
        f"Expected {epid} to be a collection ID.\n"
        "Instead, found it was of type 'Globus Connect Personal'."
    ) in result.stderr
    assert (
        "Please run the following command instead:\n\n"
        f"    globus endpoint delete {epid}"
    ) in result.stderr
