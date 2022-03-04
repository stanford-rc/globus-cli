import pytest
from globus_sdk._testing import load_response_set


def test_gcs_server_add(run_line):
    meta = load_response_set("cli.endpoint_servers").metadata
    epid = meta["endpoint_id"]
    result = run_line(f"globus endpoint server add {epid} example.org")
    assert "Server added to endpoint successfully" in result.output


def test_gcs_server_list(run_line):
    meta = load_response_set("cli.endpoint_servers").metadata
    epid = meta["endpoint_id"]
    result = run_line(f"globus endpoint server list {epid}")
    assert "gsiftp://example.org:2811" in result.output


def test_gcp_server_list(run_line):
    meta = load_response_set("cli.endpoint_servers").metadata
    epid = meta["gcp_endpoint_id"]
    result = run_line(f"globus endpoint server list {epid}")
    assert "none (Globus Connect Personal)" in result.output


@pytest.mark.parametrize("mode", ["id", "hostname", "hostname_port", "uri"])
def test_server_delete_various(run_line, mode):
    meta = load_response_set("cli.endpoint_servers").metadata
    epid = meta["endpoint_id"]

    if mode == "id":
        server = "985"
    elif mode == "hostname":
        server = "example.org"
    elif mode == "hostname_port":
        server = "example.org:2811"
    elif mode == "uri":
        server = "gsiftp://example.org:2811"
    else:
        raise NotImplementedError

    result = run_line(f"globus endpoint server delete {epid} {server}")
    assert "Server deleted successfully" in result.output


def test_server_delete_by_hostname_many_matches(run_line):
    meta = load_response_set("cli.endpoint_servers").metadata
    epid = meta["many_servers_endpoint_id"]
    server_ids = meta["many_servers_server_ids"]
    dotorg_servers = server_ids["example.org"]
    dotcom_servers = server_ids["example.com"]

    result = run_line(
        f"globus endpoint server delete {epid} example.org", assert_exit_code=2
    )
    assert "Multiple servers matched" in result.stderr
    assert "example.com" not in result.stderr
    for i in dotorg_servers:
        assert str(i) in result.stderr
    for i in dotcom_servers:
        assert str(i) not in result.stderr


def test_server_delete_on_gcp(run_line):
    meta = load_response_set("cli.endpoint_servers").metadata
    epid = meta["gcp_endpoint_id"]
    result = run_line(
        f"globus endpoint server delete {epid} example.com", assert_exit_code=2
    )
    assert (
        "You cannot delete servers from Globus Connect Personal endpoints"
        in result.stderr
    )
