import json
import uuid

import pytest
import responses
from globus_sdk._testing import load_response_set


@pytest.mark.parametrize("ep_type", ["personal", "share", "server"])
def test_endpoint_set_subscription_id(run_line, ep_type):
    meta = load_response_set("cli.endpoint_operations").metadata
    if ep_type == "personal":
        epid = meta["gcp_endpoint_id"]
    elif ep_type == "share":
        epid = meta["share_id"]
    else:
        epid = meta["endpoint_id"]
    subscription_id = str(uuid.UUID(int=0))
    run_line(f"globus endpoint set-subscription-id {epid} {subscription_id}")
    assert (
        json.loads(responses.calls[-1].request.body)["subscription_id"]
        == subscription_id
    )
