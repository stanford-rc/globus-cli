import unittest
import six
import shlex
from click.testing import CliRunner
from datetime import datetime, timedelta

import globus_sdk

from globus_cli import main
from globus_cli.config import (
    AUTH_RT_OPTNAME, AUTH_AT_OPTNAME, AUTH_AT_EXPIRES_OPTNAME,
    TRANSFER_RT_OPTNAME, TRANSFER_AT_OPTNAME, TRANSFER_AT_EXPIRES_OPTNAME,
    WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME, WHOAMI_NAME_OPTNAME,
    WHOAMI_EMAIL_OPTNAME, get_config_obj)
from globus_cli.services.transfer import get_client
from globus_cli.services.auth import get_auth_client

from tests.framework.constants import (CLITESTER1A_TRANSFER_RT,
                                       CLITESTER1A_AUTH_RT, GO_EP1_ID)
from tests.framework.tools import get_user_data


def clean_sharing():
    """
    Cleans out any files in ~/.globus/sharing/ on go#ep1 older than an hour
    TODO: remove this once deleting shared directories does full cleanup
    """
    tc = get_client()

    path = "~/.globus/sharing/"
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    filter_string = "last_modified:," + hour_ago.strftime("%Y-%m-%d %H:%M:%S")
    try:
        old_files = tc.operation_ls(
            GO_EP1_ID, path=path, filter=filter_string, num_results=None)
    except globus_sdk.TransferAPIError:
        return

    kwargs = {"notify_on_succeeded": False, "notify_on_fail": False}
    ddata = globus_sdk.DeleteData(tc, GO_EP1_ID, **kwargs)

    for item in old_files:
        ddata.add_item(path + item["name"])

    if len(ddata["DATA"]):
        tc.submit_delete(ddata)


def write_test_config(conf):
    """
    Writes known constants and refresh tokens into config for testing
    """
    user_data = get_user_data()["clitester1a"]
    testing_constants = {
        AUTH_RT_OPTNAME: CLITESTER1A_AUTH_RT,
        AUTH_AT_OPTNAME: "",
        AUTH_AT_EXPIRES_OPTNAME: 0,
        TRANSFER_RT_OPTNAME: CLITESTER1A_TRANSFER_RT,
        TRANSFER_AT_OPTNAME: "",
        TRANSFER_AT_EXPIRES_OPTNAME: 0,
        WHOAMI_ID_OPTNAME: user_data["id"],
        WHOAMI_USERNAME_OPTNAME: user_data["username"],
        WHOAMI_NAME_OPTNAME: user_data["name"],
        WHOAMI_EMAIL_OPTNAME: user_data["email"]
    }
    conf["cli"] = testing_constants
    conf.write()


class CliTestCase(unittest.TestCase):
    """
    A class of TestCases which test the CLI by making direct calls to the CLI
    and then testing the results. Uses testing refresh tokens to authorize
    calls, and wraps a click CliRunner for running commands.
    """
    def __init__(self, desc):
        unittest.TestCase.__init__(self, desc)
        self._runner = CliRunner()

    @classmethod
    def setUpClass(self):
        """
        Stores any existing config data in the cli environment of .globus.cfg
        Then replaces that data with known values for testing
        Creates a transfer client and an auth client for any direct SDK calls
        Cleans any old sharing data created by previous test runs
        """
        self.conf = get_config_obj()
        try:
            self.stored_config = self.conf["cli"]
        except KeyError:
            self.stored_config = {}
        write_test_config(self.conf)
        self.tc = get_client()
        self.ac = get_auth_client()

        clean_sharing()

    @classmethod
    def tearDownClass(self):
        """
        Restores original values of the cli environment of .globus.cfg
        """
        self.conf["cli"] = self.stored_config
        self.conf.write()

    def run_line(self, line, assert_exit_code=0, batch_input=None):
        """
        Uses the CliRunner to run the given command line,
        Asserts that the exit_code is equal to the given value
        """
        # split line into args and confirm line starts with "globus"
        # python2 shlex can't handle non ascii unicode
        if six.PY2 and isinstance(line, six.text_type):
            args = [a for a in shlex.split(line.encode("utf-8"))]
        else:
            args = shlex.split(line)
        self.assertEqual(args[0], "globus")

        # run the line. globus_cli.main is the "globus" part of the line
        # if we are expecting success (0), don't catch any exceptions.
        result = self._runner.invoke(main, args[1:], input=batch_input,
                                     catch_exceptions=bool(assert_exit_code))
        # confirm expected exit_code
        if result.exit_code != assert_exit_code:
            if isinstance(line, six.binary_type):
                line = line.decode("utf-8")
            raise(Exception(
                (u"CliTest run_line exit_code assertion failed!\n"
                 "Line: {}\nexited with {} when expecting {}\n"
                 "Output: {}".format(line, result.exit_code,
                                     assert_exit_code, result.output))))
        # return the output for further testing
        return result.output

    def run_line_no_auth(self, line, assert_exit_code=0, batch_input=None):
        """
        Wrapper around run_line that wipes the cli environment of .globus.cfg
        Before running, then restores test values after run is complete.
        """
        # wipe cli environment
        self.conf["cli"] = {}
        self.conf.write()
        # run the line in blank environment
        ret = self.run_line(line, assert_exit_code=assert_exit_code,
                            batch_input=batch_input)
        # reset the test environment and return the result
        write_test_config(self.conf)
        return ret
