import json

import pytest
import responses


@pytest.mark.parametrize("datatype_field", [None, "GIngest"])
def test_gingest_document(run_line, load_api_fixtures, tmp_path, datatype_field):
    data = load_api_fixtures("search.yaml")
    index_id = data["metadata"]["index_id"]

    data = {
        "ingest_type": "GMetaEntry",
        "ingest_data": {
            "@datatype": "GMetaEntry",
            "content": {"alpha": {"beta": "delta"}},
            "id": "testentry2",
            "subject": "http://example.com",
            "visible_to": ["public"],
        },
    }
    if datatype_field is not None:
        data["@datatype"] = "GIngest"

    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps(data))

    result, matcher = run_line(
        ["globus", "search", "ingest", index_id, str(doc)], matcher=True
    )
    matcher.check(r"^Acknowledged:\s+(\w+)$", groups=["True"])
    matcher.check(r"^Task ID:\s+([\w-]+)$")

    sent = responses.calls[-1].request
    assert sent.method == "POST"
    sent_body = json.loads(sent.body)
    assert sent_body["ingest_data"] == data["ingest_data"]


@pytest.mark.parametrize("datatype", ["GMetaEntry", "GMetaList"])
def test_auto_wrap_document(run_line, load_api_fixtures, tmp_path, datatype):
    data = load_api_fixtures("search.yaml")
    index_id = data["metadata"]["index_id"]

    entry_data = {
        "@datatype": "GMetaEntry",
        "content": {"alpha": {"beta": "delta"}},
        "id": "testentry2",
        "subject": "http://example.com",
        "visible_to": ["public"],
    }
    if datatype == "GMetaEntry":
        data = entry_data
    elif datatype == "GMetaList":
        data = {"@datatype": "GMetaList", "gmeta": [entry_data]}
    else:
        raise NotImplementedError

    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps(data))

    result, matcher = run_line(
        ["globus", "search", "ingest", index_id, str(doc)], matcher=True
    )
    matcher.check(r"^Acknowledged:\s+(\w+)$", groups=["True"])
    matcher.check(r"^Task ID:\s+([\w-]+)$")

    sent = responses.calls[-1].request
    assert sent.method == "POST"
    sent_body = json.loads(sent.body)
    assert sent_body["@datatype"] == "GIngest"
    assert sent_body["ingest_type"] == datatype
    assert sent_body["ingest_data"] == data


def test_auto_wrap_document_rejects_bad_doctype(run_line, load_api_fixtures, tmp_path):
    data = load_api_fixtures("search.yaml")
    index_id = data["metadata"]["index_id"]

    data = {
        "@datatype": "NoSuchDocumentType",
    }

    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps(data))

    result = run_line(
        ["globus", "search", "ingest", index_id, str(doc)], assert_exit_code=2
    )
    assert "Unsupported datatype: 'NoSuchDocumentType'" in result.stderr
