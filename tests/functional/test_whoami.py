def test_verbose(run_line, load_api_fixtures):
    """
    Confirms --verbose includes Name, Email, and ID fields.
    """
    data = load_api_fixtures("foo_user_info.yaml")

    result = run_line("globus whoami --verbose")
    for field in ["Username", "Name", "Email", "ID"]:
        assert field in result.output
    for field in ["username", "name", "email", "user_id"]:
        assert data["metadata"][field] in result.output


def test_linked_identities(run_line, load_api_fixtures):
    """
    Confirms --linked-identities sees foo2
    """
    data = load_api_fixtures("foo_user_info.yaml")
    username = data["metadata"]["username"]
    linked_usernames = [x["username"] for x in data["metadata"]["linked_ids"]]

    result = run_line("globus whoami --linked-identities")
    assert username in result.output
    for n in linked_usernames:
        assert n in result.output


def test_verbose_linked_identities(run_line, load_api_fixtures):
    """
    Confirms combining --verbose and --linked-identities has expected
    values present for the whole identity set.
    """
    data = load_api_fixtures("foo_user_info.yaml")
    linked_users = data["metadata"]["linked_ids"]

    result = run_line("globus whoami --linked-identities -v")

    for field in ["Username", "Name", "Email", "ID"]:
        assert field in result.output
    for field in ["username", "name", "email", "user_id"]:
        assert data["metadata"][field] in result.output
        for x in linked_users:
            assert x[field] in result.output
