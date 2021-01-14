import logging
import os
import shlex

import pytest
import responses
import six
from click.testing import CliRunner
from globus_sdk.base import slash_join
from ruamel.yaml import YAML

from globus_cli.services.auth import get_auth_client
from globus_cli.services.transfer import RetryingTransferClient
from globus_cli.services.transfer import get_client as get_transfer_client
from tests.constants import GO_EP1_ID, GO_EP2_ID
from tests.utils import patch_config

yaml = YAML()
log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_file_dir():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "files"))


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def run_line(cli_runner, request):
    """
    Uses the CliRunner to run the given command line.

    Any calls to get_config_obj during the test are patched to
    return a ConfigObj with given config dict. If no config dict is given,
    defaults to default_test_config_obj defined above.

    Asserts that the exit_code is equal to the given assert_exit_code,
    and if that exit_code is 0 prevents click from catching exceptions
    for easier debugging.
    """

    def func(line, config=None, assert_exit_code=0, stdin=None):
        from globus_cli import main

        with patch_config(config):
            # split line into args and confirm line starts with "globus"
            # python2 shlex can't handle non ascii unicode
            if six.PY2 and isinstance(line, six.text_type):
                args = [a for a in shlex.split(line.encode("utf-8"))]
            else:
                args = shlex.split(line)
            assert args[0] == "globus"

            # run the line. globus_cli.main is the "globus" part of the line
            # if we are expecting success (0), don't catch any exceptions.
            result = cli_runner.invoke(
                main, args[1:], input=stdin, catch_exceptions=bool(assert_exit_code)
            )
            assert result.exit_code == assert_exit_code, result.output
            return result

    return func


@pytest.fixture
def tc():
    with patch_config():
        return get_transfer_client()


@pytest.fixture
def ac():
    with patch_config():
        return get_auth_client()


@pytest.fixture(autouse=True)
def mocked_responses(monkeypatch):
    """
    All tests enable `responses` patching of the `requests` package, replacing
    all HTTP calls.
    """
    responses.start()

    # while request mocking is running, ensure GLOBUS_SDK_ENVIRONMENT is set to
    # production
    monkeypatch.setitem(os.environ, "GLOBUS_SDK_ENVIRONMENT", "production")

    yield

    responses.stop()
    responses.reset()


@pytest.fixture
def register_api_route(mocked_responses):
    # copied almost verbatim from the SDK testsuite
    def func(
        service,
        path,
        method=responses.GET,
        adding_headers=None,
        replace=False,
        match_querystring=False,
        **kwargs
    ):
        base_url_map = {
            "auth": "https://auth.globus.org/",
            "nexus": "https://nexus.api.globusonline.org/",
            "transfer": "https://transfer.api.globus.org/v0.10",
            "search": "https://search.api.globus.org/",
        }
        assert service in base_url_map
        base_url = base_url_map.get(service)
        full_url = slash_join(base_url, path)

        # can set it to `{}` explicitly to clear the default
        if adding_headers is None:
            adding_headers = {"Content-Type": "application/json"}

        if replace:
            responses.replace(
                method,
                full_url,
                headers=adding_headers,
                match_querystring=match_querystring,
                **kwargs
            )
        else:
            responses.add(
                method,
                full_url,
                headers=adding_headers,
                match_querystring=match_querystring,
                **kwargs
            )

    return func


@pytest.fixture
def load_api_fixtures(register_api_route, test_file_dir):
    def func(filename):
        filename = os.path.join(test_file_dir, "api_fixtures", filename)
        with open(filename) as fp:
            data = yaml.load(fp.read())
        for service, routes in data.items():
            # allow use of the key "metadata" to expose extra data from a fixture file
            # to the user of it
            if service == "metadata":
                continue
            for path, methods in routes.items():
                # allow /endpoint/{GO_EP1_ID} as a path
                path = path.format(GO_EP1_ID=GO_EP1_ID, GO_EP2_ID=GO_EP2_ID)
                for method, params in methods.items():
                    register_api_route(service, path, method=method.upper(), **params)

        # after registration, return the raw fixture data
        return data

    return func


@pytest.fixture(autouse=True)
def _reduce_transfer_client_retries(monkeypatch):
    """to make tests fail faster on network errors"""
    monkeypatch.setattr(RetryingTransferClient, "default_retries", 1)
