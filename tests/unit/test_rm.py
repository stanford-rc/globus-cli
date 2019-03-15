import json
from random import getrandbits

from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID


def _load_probably_json_substring(x):
    """
    Weak method of extracting JSON object from a string which includes JSON and
    non-JSON data. Just gets the largest substring from { to }
    Works well for these cases, where click.CliRunner gives us output
    containing both stderr and stdout.
    """
    return json.loads(x[x.index("{") : x.rindex("}") + 1])


class RMTests(CliTestCase):
    def test_recursive(self):
        """
        Makes a dir on ep1, then --recursive rm's it.
        Confirms delete task was successful.
        """
        # name randomized to prevent collision
        path = "/~/rm_dir-{}".format(str(getrandbits(128)))
        self.tc.operation_mkdir(GO_EP1_ID, path)

        output = self.run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, path))
        res = _load_probably_json_substring(output)
        self.assertEqual(res["status"], "SUCCEEDED")

    def test_no_file(self):
        """
        Attempts to remove a non-existant file. Confirms exit code 1
        """
        path = "/~/nofilehere.txt"
        self.run_line("globus rm {}:{}".format(GO_EP1_ID, path), assert_exit_code=1)

    def test_ignore_missing(self):
        """
        Attempts to remove a non-existant file path, with --ignore-missing.
        Confirms exit code 0 and silent output.
        """
        path = "/~/nofilehere.txt"
        output = self.run_line("globus rm -f {}:{}".format(GO_EP1_ID, path))
        self.assertIn("Delete task submitted under ID ", output)

    def test_pattern_globbing(self):
        """
        Makes 3 dirs with the same prefix, and uses * globbing to rm them all.
        Confirms delete task was successful and removed 3 dirs.
        """
        # mark all dirs with a random generated prefix to prevent collision
        rand = str(getrandbits(128))
        for i in range(3):
            path = "/~/rm_dir{}-{}".format(rand, i)
            self.tc.operation_mkdir(GO_EP1_ID, path)

        # remove all dirs with the prefix
        glob = "rm_dir{}*".format(rand)
        output = self.run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, glob))
        res = _load_probably_json_substring(output)
        self.assertEqual(res["status"], "SUCCEEDED")

        # confirm no dirs with the prefix exist on the endpoint
        filter_string = "name:~rm_dir{}*".format(rand)
        ls_doc = self.tc.operation_ls(GO_EP1_ID, filter=filter_string)
        self.assertEquals(list(ls_doc), [])

    def test_wild_globbing(self):
        """
        Makes 3 dirs with the same prefix, and uses ? globbing to rm them all.
        Confirms delete task was successful and removed 3 dirs.
        """
        # mark all dirs with a random generated prefix to prevent collision
        rand = str(getrandbits(128))
        for i in range(3):
            path = "/~/rm_dir{}-{}".format(rand, i)
            self.tc.operation_mkdir(GO_EP1_ID, path)

        # remove all dirs with the prefix
        glob = "rm_dir{}-?".format(rand)
        output = self.run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, glob))
        res = _load_probably_json_substring(output)
        self.assertEqual(res["status"], "SUCCEEDED")

        # confirm no dirs with the prefix exist on the endpoint
        filter_string = "name:~rm_dir{}*".format(rand)
        ls_doc = self.tc.operation_ls(GO_EP1_ID, filter=filter_string)
        self.assertEquals(list(ls_doc), [])

    def test_bracket_globbing(self):
        """
        Makes 3 dirs with the same prefix, and uses [] globbing to rm them all.
        Confirms delete task was successful and removed 3 dirs.
        """
        # mark all dirs with a random generated prefix to prevent collision
        rand = str(getrandbits(128))
        for i in range(3):
            path = "/~/rm_dir{}-{}".format(rand, i)
            self.tc.operation_mkdir(GO_EP1_ID, path)

        # remove all dirs with the prefix
        glob = "rm_dir{}-[012]".format(rand)
        output = self.run_line("globus rm -r -F json {}:{}".format(GO_EP1_ID, glob))
        res = _load_probably_json_substring(output)
        self.assertEqual(res["status"], "SUCCEEDED")

        # confirm no dirs with the prefix exist on the endpoint
        filter_string = "name:~rm_dir{}*".format(rand)
        ls_doc = self.tc.operation_ls(GO_EP1_ID, filter=filter_string)
        self.assertEquals(list(ls_doc), [])

    def test_timeout(self):
        """
        Attempts to remove a path we are not allowed to remove,
        confirms rm times out and exits 1 after given timeout.
        """
        timeout = 2
        path = "/share/godata/file1.txt"
        output = self.run_line(
            "globus rm -r --timeout {} {}:{}".format(timeout, GO_EP1_ID, path),
            assert_exit_code=1,
        )
        self.assertIn(
            ("Task has yet to complete " "after {} seconds".format(timeout)), output
        )

    def test_timeout_explicit_status(self):
        """
        Attempts to remove a path we are not allowed to remove,
        confirms rm times out and exits STATUS after given timeout, where
        STATUS is set via the --timeout-exit-code opt
        """
        timeout = 1
        status = 50
        path = "/share/godata/file1.txt"
        output = self.run_line(
            "globus rm -r --timeout {} --timeout-exit-code {} {}:{}".format(
                timeout, status, GO_EP1_ID, path
            ),
            assert_exit_code=status,
        )
        self.assertIn(
            ("Task has yet to complete " "after {} seconds".format(timeout)), output
        )
