import functools

import click

from .tokenstore import token_storage_adapter


class LoginManager:
    def __init__(self):
        self._token_storage = token_storage_adapter()

    def has_login(self, resource_server: str):
        """
        Determines if the user has a refresh token for the given
        resource server
        """
        tokens = self._token_storage.get_token_data(resource_server)
        if tokens is None or "refresh_token" not in tokens:
            return False

        return True


def requires_login(*args: str, pass_manager: bool = False):
    """
    Command decorator for specifying a resource server that the user must have
    tokens for in order to run the command.

    Simple usage for commands that have static resource needs: simply list all
    needed resource servers as args:

    @requries_login("auth.globus.org")

    @requires_login("auth.globus.org", "transfer.api.globus.org")

    Usage for commands which have dynamic resource servers depending
    on the arguments passed to the command (e.g. commands for the GCS API)

    @requies_login(pass_manager=True)
    def command(login_manager, endpoint_id)

        login_manager.<do the thing>(endpoint_id)

    """
    resource_servers = args

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            manager = LoginManager()

            # determine the set of resource servers missing logins
            missing_servers = set()
            for server_name in resource_servers:
                if not manager.has_login(server_name):
                    missing_servers.add(server_name)

            # if we are missing logins, assemble error text
            # text is slightly different for 1, 2, or 3+ missing servers
            if missing_servers:

                if len(missing_servers) == 1:
                    plural_string = ""
                    server_string = missing_servers.pop()

                elif len(missing_servers) == 2:
                    plural_string = "s"
                    server_string = "{} and {}".format(
                        missing_servers.pop(), missing_servers.pop()
                    )

                else:
                    plural_string = "s"
                    single_server = missing_servers.pop()
                    server_string = ", ".join(missing_servers) + ", and {}".format(
                        single_server
                    )

                raise click.ClickException(
                    "Missing login{} for {}, please run 'globus login'".format(
                        plural_string, server_string
                    )
                )

            # if pass_manager is True, pass it as an additional positional arg
            if pass_manager:
                return func(*args, manager, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return inner
