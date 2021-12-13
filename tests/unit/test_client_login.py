import globus_sdk
import pytest

from globus_cli.login_manager import get_client_login, is_client_login
from globus_cli.login_manager.tokenstore import _resolve_namespace


def test_is_client_login_success(client_login):
    assert is_client_login() is True


def test_is_client_login_no_login():
    assert is_client_login() is False


def test_is_client_login_no_secret(client_login_no_secret):
    with pytest.raises(ValueError):
        is_client_login()


def test_get_client_login_success(client_login):
    client = get_client_login()
    assert isinstance(client, globus_sdk.ConfidentialAppAuthClient)
    assert client.authorizer.username == "fake_client_id"
    assert client.authorizer.password == "fake_client_secret"


def test_get_client_login_no_login():
    with pytest.raises(ValueError):
        get_client_login()


def test_get_client_login_no_secret(client_login_no_secret):
    with pytest.raises(ValueError):
        get_client_login()


def test_client_namespace(client_login):
    assert _resolve_namespace() == "clientprofile/production"
