def test_task_show(run_line, load_api_fixtures):
    data = load_api_fixtures("search.yaml")
    task_id = data["metadata"]["task_id"]

    result = run_line(["globus", "search", "task", "show", task_id])
    assert "SUCCESS (Task succeeded)" in result.output


def test_task_list(run_line, load_api_fixtures):
    data = load_api_fixtures("search.yaml")
    index_id = data["metadata"]["index_id"]
    success_task_id = data["metadata"]["task_id"]
    pending_task_id = data["metadata"]["pending_task_id"]

    result = run_line(["globus", "search", "task", "list", index_id])

    found_success, found_pending = False, False
    for line in result.output.split("\n"):
        if success_task_id in line:
            found_success = True
            assert "SUCCESS" in line
        elif pending_task_id in line:
            found_pending = True
            assert "PENDING" in line
    assert found_success
    assert found_pending
