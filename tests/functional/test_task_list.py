def test_task_list_success(run_line, load_api_fixtures):
    load_api_fixtures("task_list.yaml")
    result = run_line("globus task list")
    assert "SUCCEEDED" in result.output
    assert "TRANSFER" in result.output
