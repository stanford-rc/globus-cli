def test_index_list(run_line, load_api_fixtures):
    data = load_api_fixtures("search.yaml")
    list_data = data["metadata"]["index_list_data"]

    result = run_line(["globus", "search", "index", "list"])

    found = set()
    for index_id, attrs in list_data.items():
        for line in result.output.split("\n"):
            if index_id in line:
                found.add(index_id)
                for v in attrs.values():
                    assert v in line
    assert len(found) == len(list_data)


def test_index_show(run_line, load_api_fixtures):
    data = load_api_fixtures("search.yaml")
    index_id = data["metadata"]["index_id"]

    result, matcher = run_line(
        ["globus", "search", "index", "show", index_id], matcher=True
    )
    matcher.check(r"^Index ID:\s+([\w-]+)$", groups=[index_id])


def test_index_create(run_line, load_api_fixtures):
    data = load_api_fixtures("search.yaml")
    index_id = data["metadata"]["index_id"]

    result, matcher = run_line(
        [
            "globus",
            "search",
            "index",
            "create",
            "example_cookery",
            "Example index of Cookery",
        ],
        matcher=True,
    )
    matcher.check(r"^Index ID:\s+([\w-]+)$", groups=[index_id])
