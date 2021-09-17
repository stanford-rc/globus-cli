def test_group_list(run_line, load_api_fixtures, go_ep1_id):
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
