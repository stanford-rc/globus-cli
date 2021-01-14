import logging
import os
import shlex

import pytest
import responses
import six
from click.testing import CliRunner

from globus_cli.services.auth import get_auth_client
from globus_cli.services.transfer import get_client as get_transfer_client
from tests.utils import patch_config

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
            assert result.exit_code == assert_exit_code
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
def mocked_responses():
    """
    All tests enable `responses` patching of the `requests` package, replacing
    all HTTP calls.
    """
    responses.start()

    yield

    responses.stop()
    responses.reset()
