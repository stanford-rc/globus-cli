import pytest


@pytest.mark.parametrize(
    "cli_argument", ("42277910-0c18-11ec-ba76-138ac5bdb19f", "--all")
)
def test_cancel(run_line, load_api_fixtures, cli_argument):
    """Validate task cancellation."""

    load_api_fixtures("task_cancel.yaml")
    result = run_line(f"globus task cancel {cli_argument}")
    assert "cancelled successfully" in result.output
