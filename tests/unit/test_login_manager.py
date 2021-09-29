import re
import uuid
from unittest.mock import patch

import pytest

from globus_cli.login_manager import LoginManager, MissingLoginError


def mock_get_tokens(resource_server):
    fake_tokens = {
        "a.globus.org": {
            "access_token": "fake_a_access_token",
            "refresh_token": "fake_a_refresh_token",
        },
        "b.globus.org": {
            "access_token": "fake_b_access_token",
            "refresh_token": "fake_b_refresh_token",
        },
    }

    return fake_tokens.get(resource_server)


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_requires_login_success(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens

    # single server
    @LoginManager.requires_login("a.globus.org")
    def dummy_command():
        return True

    assert dummy_command()


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_requires_login_multi_server_success(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens

    @LoginManager.requires_login("a.globus.org", "b.globus.org")
    def dummy_command():
        return True

    assert dummy_command()


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_requires_login_single_server_fail(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens

    @LoginManager.requires_login("c.globus.org")
    def dummy_command():
        return True

    with pytest.raises(MissingLoginError) as ex:
        dummy_command()

    assert str(ex.value) == (
        "Missing login for c.globus.org, please run\n\n  globus login\n"
    )


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_requires_login_fail_two_servers(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens

    @LoginManager.requires_login("c.globus.org", "d.globus.org")
    def dummy_command():
        return True

    with pytest.raises(MissingLoginError) as ex:
        dummy_command()

    assert re.match(
        "Missing logins for ..globus.org and ..globus.org, "
        "please run\n\n  globus login\n",
        str(ex.value),
    )
    for server in ("c.globus.org", "d.globus.org"):
        assert server in str(ex.value)


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_requires_login_fail_multi_server(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens

    @LoginManager.requires_login("c.globus.org", "d.globus.org", "e.globus.org")
    def dummy_command():
        return True

    with pytest.raises(MissingLoginError) as ex:
        dummy_command()

    assert re.search(
        "Missing logins for ..globus.org, ..globus.org, and ..globus.org", str(ex.value)
    )
    assert "globus login\n" in str(ex.value)
    for server in ("c.globus.org", "d.globus.org", "e.globus.org"):
        assert server in str(ex.value)


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_requires_login_pass_manager(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens

    @LoginManager.requires_login(pass_manager=True)
    def dummy_command(manager):

        assert manager.has_login("a.globus.org")
        assert not manager.has_login("c.globus.org")

        return True

    assert dummy_command()


@patch("globus_cli.login_manager.tokenstore.token_storage_adapter")
def test_gcs_error_message(mock_get_adapter):
    mock_get_adapter._instance.get_token_data = mock_get_tokens
    dummy_id = str(uuid.uuid1())

    @LoginManager.requires_login(pass_manager=True)
    def dummy_command(manager):
        manager.assert_logins(dummy_id, assume_gcs=True)

    with pytest.raises(MissingLoginError) as excinfo:
        dummy_command()

    assert f"globus login --gcs {dummy_id}" in str(excinfo.value)
