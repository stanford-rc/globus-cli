def test_task_event_list_success(run_line, load_api_fixtures):
    data = load_api_fixtures("task_event_list.yaml")
    task_id = data["metadata"]["task_id"]
    result = run_line(f"globus task event-list {task_id}")
    assert "Canceled by the task owner" in result.output
