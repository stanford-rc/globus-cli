import json
import uuid

import pytest
import responses


@pytest.mark.parametrize(
    "ep_type",
    ["personal", "share", "server"],
)
def test_endpoint_set_subscription_id(run_line, load_api_fixtures, ep_type):
    data = load_api_fixtures("endpoint_operations.yaml")
    if ep_type == "personal":
        epid = data["metadata"]["gcp_endpoint_id"]
    elif ep_type == "share":
        epid = data["metadata"]["share_id"]
    else:
        epid = data["metadata"]["endpoint_id"]
    subscription_id = str(uuid.UUID(int=0))
    run_line(f"globus endpoint set-subscription-id {epid} {subscription_id}")
    assert (
        json.loads(responses.calls[-1].request.body)["subscription_id"]
        == subscription_id
    )
