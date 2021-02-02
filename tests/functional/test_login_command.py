from unittest import mock

import globus_sdk

from globus_cli.config import AUTH_RT_OPTNAME, TRANSFER_RT_OPTNAME


def test_login_validates_token(run_line, default_test_config):
    with mock.patch("globus_cli.commands.login.internal_auth_client") as m:
        ac = mock.MagicMock(spec=globus_sdk.NativeAppAuthClient)
        m.return_value = ac

        run_line("globus login")

        a_rt = default_test_config["cli"][AUTH_RT_OPTNAME]
        t_rt = default_test_config["cli"][TRANSFER_RT_OPTNAME]
        ac.oauth2_validate_token.assert_any_call(a_rt)
        ac.oauth2_validate_token.assert_any_call(t_rt)
