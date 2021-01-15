import logging
import os
import shlex
import time

import pytest
import responses
import six
from click.testing import CliRunner
from configobj import ConfigObj
from globus_sdk.base import slash_join
from ruamel.yaml import YAML

import globus_cli.config
from globus_cli.services.transfer import RetryingTransferClient
from tests.constants import GO_EP1_ID, GO_EP2_ID

yaml = YAML()
log = logging.getLogger(__name__)


@pytest.fixture
def default_test_config():
    """
    Returns a ConfigObj with the clitester's refresh tokens as if the
    clitester was logged in and a call to get_config_obj was made.
    """
    # create a ConfgObj from a dict of testing constants. a ConfigObj created
    # this way will not be tied to a config file on disk, meaning that
    # ConfigObj.filename = None and ConfigObj.write() returns a string without
    # writing anything to disk.
    return ConfigObj(
        {
            "cli": {
                globus_cli.config.CLIENT_ID_OPTNAME: "fakeClientIDString",
                globus_cli.config.CLIENT_SECRET_OPTNAME: "fakeClientSecret",
                globus_cli.config.AUTH_RT_OPTNAME: "AuthRT",
                globus_cli.config.AUTH_AT_OPTNAME: "AuthAT",
                globus_cli.config.AUTH_AT_EXPIRES_OPTNAME: int(time.time()) + 120,
                globus_cli.config.TRANSFER_RT_OPTNAME: "TransferRT",
                globus_cli.config.TRANSFER_AT_OPTNAME: "TransferAT",
                globus_cli.config.TRANSFER_AT_EXPIRES_OPTNAME: int(time.time()) + 120,
            }
        }
    )


@pytest.fixture
def patch_config(monkeypatch, default_test_config):
    def func(conf=None):
        if conf is None:
            conf = default_test_config

        def mock_get_config():
            return conf

        monkeypatch.setattr(globus_cli.config, "get_config_obj", mock_get_config)

    return func


@pytest.fixture(scope="session")
def test_file_dir():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "files"))


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def run_line(cli_runner, request, patch_config):
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

        patch_config(config)

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
        if result.exit_code != assert_exit_code:
            log.error(
                "network calls:\n%s",
                "\n".join(r.request.url for r in responses.calls),
            )
        assert result.exit_code == assert_exit_code, result.output
        return result

    return func


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


def _iter_fixture_routes(routes):
    # walk a fixture file either as a nested dict or list of routes
    # lists allow us to workaround duplicates when they only differ by params
    if isinstance(routes, list):
        for x in routes:
            # copy and remove elements
            params = {**x}
            path = params.pop("path")
            method = params.pop("method")
            yield path, method, params
    else:
        for path, methods in routes.items():
            for method, params in methods.items():
                yield path, method, params


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

            for path, method, params in _iter_fixture_routes(routes):
                # allow /endpoint/{GO_EP1_ID} as a path
                use_path = path.format(GO_EP1_ID=GO_EP1_ID, GO_EP2_ID=GO_EP2_ID)
                if "query_params" in params:
                    # copy and set match_querystring=True
                    params = {"match_querystring": True, **params}
                    # remove and encode query params
                    query_params = six.moves.urllib.parse.urlencode(
                        params.pop("query_params")
                    )
                    # modify path (assume no prior params)
                    use_path = use_path + "?" + query_params
                register_api_route(service, use_path, method=method.upper(), **params)

        # after registration, return the raw fixture data
        return data

    return func


@pytest.fixture(autouse=True)
def _reduce_transfer_client_retries(monkeypatch):
    """to make tests fail faster on network errors"""
    monkeypatch.setattr(RetryingTransferClient, "default_retries", 1)
