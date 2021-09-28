def test_collection_list(run_line, load_api_fixtures, add_gcs_login):
    data = load_api_fixtures("collection_operations.yaml")
    epid = data["metadata"]["endpoint_id"]
    add_gcs_login(epid)
    result = run_line(f"globus collection list {epid}")
    collection_names = ["Happy Fun Collection Name 1", "Happy Fun Collection Name 2"]
    for name in collection_names:
        assert name in result.stdout
