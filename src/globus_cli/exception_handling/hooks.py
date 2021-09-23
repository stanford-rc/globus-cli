from typing import List, Union, cast

import click
import globus_sdk

from globus_cli.endpointish import WrongEndpointTypeError
from globus_cli.termio import PrintableErrorField, write_error_info

from .registry import error_handler


@error_handler(
    error_class=globus_sdk.GlobusAPIError,
    condition=lambda err: err.info.authorization_parameters,
)
def session_hook(exception: globus_sdk.GlobusAPIError) -> None:
    """
    Expects an exception with a valid authorization_paramaters info field
    """
    click.echo(
        "The resource you are trying to access requires you to "
        "re-authenticate with specific identities."
    )

    message = exception.info.authorization_parameters.session_message
    if message:
        click.echo(f"message: {message}")

    identities = exception.info.authorization_parameters.session_required_identities
    domains = exception.info.authorization_parameters.session_required_single_domain
    if identities or domains:
        # cast: mypy can't deduce that `domains` is not None if `identities` is None
        update_target = (
            " ".join(identities)
            if identities is not None
            else " ".join(cast(List[str], domains))
        )
        click.echo(
            "Please run\n\n"
            f"    globus session update {update_target}\n\n"
            "to re-authenticate with the required identities"
        )
    else:
        click.echo(
            'Please use "globus session update" to re-authenticate '
            "with specific identities"
        )


@error_handler(
    error_class=globus_sdk.GlobusAPIError,
    condition=lambda err: err.info.consent_required,
)
def consent_required_hook(exception: globus_sdk.GlobusAPIError) -> None:
    """
    Expects an exception with a required_scopes field in its raw_json
    """
    # specialized message for data_access errors
    # otherwise, use more generic phrasing
    if exception.message == "Missing required data_access consent":
        click.echo(
            "The collection you are trying to access data on requires you to "
            "grant consent for the Globus CLI to access it."
        )
    else:
        click.echo(
            "The resource you are trying to access requires you to "
            "consent to additional access for the Globus CLI."
        )
    click.echo(f"message: {exception.message}")

    required_scopes = exception.info.consent_required.required_scopes
    if not required_scopes:
        click.secho(
            "Fatal Error: ConsentRequired but no required_scopes!", bold=True, fg="red"
        )
        click.get_current_context().exit(255)
    else:
        click.echo(
            "\nPlease run\n\n"
            "  globus session consent {}\n\n".format(
                " ".join(f"'{x}'" for x in required_scopes)
            )
            + "to login with the required scopes"
        )


@error_handler(
    condition=lambda err: (
        (
            isinstance(err, globus_sdk.TransferAPIError)
            and err.code == "ClientError.AuthenticationFailed"
        )
        or (isinstance(err, globus_sdk.AuthAPIError) and err.code == "UNAUTHORIZED")
    )
)
def authentication_hook(
    exception: Union[globus_sdk.TransferAPIError, globus_sdk.AuthAPIError]
) -> None:
    write_error_info(
        "No Authentication Error",
        [
            PrintableErrorField("HTTP status", exception.http_status),
            PrintableErrorField("code", exception.code),
            PrintableErrorField("message", exception.message, multiline=True),
        ],
        message=(
            "Globus CLI Error: No Authentication provided. Make sure "
            "you have logged in with 'globus login'."
        ),
    )


@error_handler(error_class=globus_sdk.TransferAPIError)
def transferapi_hook(exception: globus_sdk.TransferAPIError) -> None:
    write_error_info(
        "Transfer API Error",
        [
            PrintableErrorField("HTTP status", exception.http_status),
            PrintableErrorField("request_id", exception.request_id),
            PrintableErrorField("code", exception.code),
            PrintableErrorField("message", exception.message, multiline=True),
        ],
    )


@error_handler(
    error_class=globus_sdk.AuthAPIError,
    condition=lambda err: err.message == "invalid_grant",
)
def invalidrefresh_hook(exception: globus_sdk.AuthAPIError) -> None:
    write_error_info(
        "Invalid Refresh Token",
        [
            PrintableErrorField("HTTP status", exception.http_status),
            PrintableErrorField("code", exception.code),
            PrintableErrorField("message", exception.message, multiline=True),
        ],
        message=(
            "Globus CLI Error: Your credentials are no longer "
            "valid. Please log in again with 'globus login'."
        ),
    )


@error_handler(error_class=globus_sdk.AuthAPIError)
def authapi_hook(exception: globus_sdk.AuthAPIError) -> None:
    write_error_info(
        "Auth API Error",
        [
            PrintableErrorField("HTTP status", exception.http_status),
            PrintableErrorField("code", exception.code),
            PrintableErrorField("message", exception.message, multiline=True),
        ],
    )


@error_handler(error_class=globus_sdk.GlobusAPIError)  # catch-all
def globusapi_hook(exception: globus_sdk.GlobusAPIError) -> None:
    write_error_info(
        "Globus API Error",
        [
            PrintableErrorField("HTTP status", exception.http_status),
            PrintableErrorField("code", exception.code),
            PrintableErrorField("message", exception.message, multiline=True),
        ],
    )


@error_handler(error_class=globus_sdk.GlobusError)
def globus_error_hook(exception: globus_sdk.GlobusError) -> None:
    write_error_info(
        "Globus Error",
        [
            PrintableErrorField("error_type", exception.__class__.__name__),
            PrintableErrorField("message", str(exception), multiline=True),
        ],
    )


@error_handler(error_class=WrongEndpointTypeError)
def wrong_endpoint_type_error_hook(exception: WrongEndpointTypeError) -> None:
    ctx = click.get_current_context()

    click.echo(
        click.style(
            exception.expected_message + "\n" + exception.actual_message,
            fg="yellow",
        )
        + "\n\n",
        err=True,
    )

    should_use = exception.should_use_command()
    if should_use:
        click.echo(
            "Please run the following command instead:\n\n"
            f"    {should_use} {exception.endpoint_id}\n",
            err=True,
        )
    else:
        click.echo(
            click.style(
                "This operation is not supported on objects of this type.",
                fg="red",
                bold=True,
            ),
            err=True,
        )
    ctx.exit(2)


def register_all_hooks() -> None:
    """
    This is a stub method which does nothing.

    Importing and running it serves to ensure that the various hooks were imported,
    however. It therefore "looks imperative" and ensures that the hooks are loaded.
    """
