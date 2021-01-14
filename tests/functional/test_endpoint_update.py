import json

import pytest
import responses


@pytest.mark.parametrize(
    "ep_type",
    ["personal", "share", "server"],
)
def test_general_options(run_line, load_api_fixtures, ep_type):
    """
    Runs endpoint update with parameters allowed for all endpoint types
    Confirms all endpoint types are successfully updated
    """
    data = load_api_fixtures("endpoint_operations.yaml")
    if ep_type == "personal":
        epid = data["metadata"]["gcp_endpoint_id"]
    elif ep_type == "share":
        epid = data["metadata"]["share_id"]
    else:
        epid = data["metadata"]["endpoint_id"]

    # options with option value and expected value
    # if expected value is not set, it will be copied from the option value
    option_dicts = [
        {"opt": "--display-name", "key": "display_name", "val": "newname"},
        {"opt": "--description", "key": "description", "val": "newtext"},
        {"opt": "--default-directory", "key": "default_directory", "val": "/share/"},
        {"opt": "--organization", "key": "organization", "val": "neworg"},
        {"opt": "--department", "key": "department", "val": "newdept"},
        {"opt": "--keywords", "key": "keywords", "val": "new,key,words"},
        {"opt": "--contact-email", "key": "contact_email", "val": "a@b.c"},
        {"opt": "--contact-info", "key": "contact_info", "val": "newinfo"},
        {"opt": "--info-link", "key": "info_link", "val": "http://a.b"},
        {
            "opt": "--force-encryption",
            "key": "force_encryption",
            "val": None,
            "expected": True,
        },
        {
            "opt": "--disable-verify",
            "key": "disable_verify",
            "val": None,
            "expected": True,
        },
    ]
    if ep_type == "server":
        option_dicts.extend(
            [
                {"opt": "--myproxy-dn", "key": "myproxy_dn", "val": "/dn"},
                {
                    "opt": "--myproxy-server",
                    "key": "myproxy_server",
                    "val": "srv.example.com",
                },
                {"opt": "--private", "key": "public", "val": None, "expected": False},
                {
                    "opt": "--location",
                    "key": "location",
                    "val": "1.1,2",
                    "expected": "1.1,2",
                },
            ]
        )

    for x in option_dicts:
        if "expected" not in x:
            x["expected"] = x["val"]

    # make and run the line
    line = ["globus", "endpoint", "update", epid, "-F", "json"]
    for item in option_dicts:
        line.append(item["opt"])
        if item["val"]:
            line.append(item["val"])
    run_line(" ".join(line))

    # get and confirm values which were sent as JSON
    sent_data = json.loads(responses.calls[-1].request.body)
    for item in option_dicts:
        assert item["expected"] == sent_data[item["key"]]


@pytest.mark.parametrize(
    "ep_type",
    ["personal", "share"],
)
def test_invalid_gcs_only_options(run_line, load_api_fixtures, ep_type):
    """
    For all GCS only options, tries to update a GCP and shared endpoint
    Confirms invalid options are caught at the CLI level rather than API
    """
    data = load_api_fixtures("endpoint_operations.yaml")
    if ep_type == "personal":
        epid = data["metadata"]["gcp_endpoint_id"]
    elif ep_type == "share":
        epid = data["metadata"]["share_id"]
    else:
        raise NotImplementedError
    options = [
        "--public",
        "--private",
        "--myproxy-dn /dn",
        "--myproxy-server mpsrv.example.com",
        "--oauth-server oasrv.example.com",
        "--location 1,1",
    ]
    for opt in options:
        result = run_line(
            ("globus endpoint update {} {} ".format(epid, opt)),
            assert_exit_code=2,
        )
        assert "Globus Connect Server" in result.output


def test_invalid_managed_only_options(run_line, load_api_fixtures):
    """
    For all managed only options, tries to update a GCS endpoint
    Confirms invalid options are caught at the CLI level rather than AP
    """
    data = load_api_fixtures("endpoint_operations.yaml")
    epid = data["metadata"]["endpoint_id"]

    options = [
        "--network-use custom",
        "--max-concurrency 2",
        "--preferred-concurrency 1",
        "--max-parallelism 2",
        "--preferred-parallelism 1",
    ]
    for opt in options:
        result = run_line(
            ("globus endpoint update {} {} ".format(epid, opt)),
            assert_exit_code=2,
        )
        assert "managed endpoints" in result.output
