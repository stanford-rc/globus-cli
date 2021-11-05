import responses


def test_task_list_success(run_line, load_api_fixtures):
    load_api_fixtures("task_list.yaml")
    result = run_line("globus task list")
    assert "SUCCEEDED" in result.output
    assert "TRANSFER" in result.output
    # check that empty filters aren't passed through
    filters = dict(
        x.split(":") for x in responses.calls[0].request.params["filter"].split("/")
    )
    assert "completion_time" not in filters
    assert "request_time" not in filters
