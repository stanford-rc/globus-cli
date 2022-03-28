import os


def test_webapp_url_in_endpoint_activation_is_env_sensitive(
    run_line, monkeypatch, go_ep1_id
):
    command = [
        "globus",
        "endpoint",
        "activate",
        "--web",
        "--no-browser",
        "--force",
        "--no-autoactivate",
        go_ep1_id,
    ]
    result = run_line(command)
    assert "https://app.globus.org/file-manager" in result.output

    monkeypatch.setitem(os.environ, "GLOBUS_SDK_ENVIRONMENT", "preview")
    result = run_line(command)
    assert "https://app.preview.globus.org/file-manager" in result.output
