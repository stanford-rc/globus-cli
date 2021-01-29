def test_skipped_errors(run_line, load_api_fixtures, task_id):
    """
    Confirms --skipped-errors option for task show parses the output of
    GET /task/<task_id>/skipped_errors
    """
    load_api_fixtures("skipped_error_list.yaml")

    result = run_line("globus task show --skipped-errors {}".format(task_id))
    assert "/~/no-such-file" in result.output
    assert "FILE_NOT_FOUND" in result.output
    assert "/~/restricted-file" in result.output
    assert "PERMISSION_DENIED" in result.output
