from tests.framework.cli_testcase import CliTestCase
from tests.framework.tools import get_user_data


class WhoamiTests(CliTestCase):

    # basic whoami functionality tested in test_basics.py

    def test_verbose(self):
        """
        Confirms --verbose includes Name, Email, and ID fields.
        """
        output = self.run_line("globus whoami --verbose")
        for field in ["Username", "Name", "Email", "ID"]:
            self.assertIn(field, output)
        for field in ["username", "name", "email", "id"]:
            self.assertIn(get_user_data()["clitester1a"][field], output)

    def test_linked_identities(self):
        """
        Confirms --linked-identities sees cliester1a-linked#globusid.org
        """
        output = self.run_line("globus whoami --linked-identities")
        self.assertIn(get_user_data()["clitester1a"]["username"], output)
        self.assertIn(get_user_data()["clitester1alinked"]["username"], output)

    def test_verbose_linked_identities(self):
        """
        Confirms combining --verbose and --linked-identities has expected
        values present for the whole identity set.
        """
        output = self.run_line("globus whoami --linked-identities -v")
        for field in ["Username", "Name", "Email", "ID"]:
            self.assertIn(field, output)
        for field in ["username", "name", "email", "id"]:
            self.assertIn(get_user_data()["clitester1a"][field], output)
            self.assertIn(get_user_data()["clitester1alinked"][field], output)
