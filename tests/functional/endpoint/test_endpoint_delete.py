import json


def test_simple_deletion(run_line, load_api_fixtures):
    data = load_api_fixtures("endpoint_operations.yaml")
    epid = data["metadata"]["endpoint_id"]
    result = run_line(f"globus endpoint delete {epid} -F json")

    res = json.loads(result.output)
    assert res["DATA_TYPE"] == "result"
    assert res["code"] == "Deleted"
    assert res["message"] == "Endpoint deleted successfully"


def test_delete_gcs_guest_collection(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["guest_collection_id"]
    result = run_line(f"globus endpoint delete {epid}", assert_exit_code=2)

    assert "success" not in result.output
    assert (
        f"Expected {epid} to be an endpoint ID.\n"
        "Instead, found it was of type 'Guest Collection'."
    ) in result.stderr
    assert (
        "Please run the following command instead:\n\n"
        f"    globus collection delete {epid}"
    ) in result.stderr


def test_delete_gcs_mapped_collection(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["mapped_collection_id"]
    result = run_line(f"globus endpoint delete {epid}", assert_exit_code=2)

    assert "success" not in result.output
    assert (
        f"Expected {epid} to be an endpoint ID.\n"
        "Instead, found it was of type 'Mapped Collection'."
    ) in result.stderr
    assert (
        "Please run the following command instead:\n\n"
        f"    globus collection delete {epid}"
    ) in result.stderr


def test_delete_gcsv5_endpoint(run_line, load_api_fixtures):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]
    result = run_line(f"globus endpoint delete {epid}", assert_exit_code=2)

    assert "success" not in result.output
    assert (
        f"Expected {epid} to be an endpoint ID.\n"
        "Instead, found it was of type 'Globus Connect Server v5 Endpoint'."
    ) in result.stderr
    assert "This operation is not supported on objects of this type." in result.stderr
