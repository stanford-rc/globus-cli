try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk

from tests.framework.cli_testcase import CliTestCase

from globus_cli.config import AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME


class EndpointCreateTests(CliTestCase):
    @mock.patch('globus_cli.commands.login.internal_auth_client')
    def test_login_validates_token(self, get_client):
        ac = mock.MagicMock(spec=globus_sdk.NativeAppAuthClient)
        get_client.return_value = ac

        self.run_line("globus login")

        a_rt = self.conf['cli'][AUTH_RT_OPTNAME]
        t_rt = self.conf['cli'][TRANSFER_RT_OPTNAME]
        ac.oauth2_validate_token.assert_any_call(a_rt)
        ac.oauth2_validate_token.assert_any_call(t_rt)
