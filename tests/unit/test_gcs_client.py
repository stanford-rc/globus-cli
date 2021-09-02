import uuid

import pytest

from globus_cli.services.gcs import get_gcs_client


def test_get_gcs_client_missing_required_auth():
    gcsid = str(uuid.uuid1())

    with pytest.raises(ValueError) as excinfo:
        get_gcs_client(gcsid)

    assert f"--gcs {gcsid}" in str(excinfo.value)
