import click

from globus_cli.parsing import command, endpoint_id_arg, security_principal_opts
from globus_cli.safeio import formatted_print
from globus_cli.services.auth import maybe_lookup_identity_id
from globus_cli.services.transfer import assemble_generic_doc, get_client


@command("create")
@endpoint_id_arg
@security_principal_opts(allow_provision=True)
@click.option(
    "--role",
    required=True,
    type=click.Choice(
        ("administrator", "access_manager", "activity_manager", "activity_monitor"),
        case_sensitive=False,
    ),
    help="A role to assign.",
)
def role_create(role, principal, endpoint_id):
    """Create a role on an endpoint"""
    principal_type, principal_val = principal

    client = get_client()

    if principal_type == "identity":
        principal_val = maybe_lookup_identity_id(principal_val)
        if not principal_val:
            raise click.UsageError(
                "Identity does not exist. "
                "Use --provision-identity to auto-provision an identity."
            )
    elif principal_type == "provision-identity":
        principal_val = maybe_lookup_identity_id(principal_val, provision=True)
        principal_type = "identity"

    role_doc = assemble_generic_doc(
        "role", principal_type=principal_type, principal=principal_val, role=role
    )

    res = client.add_endpoint_role(endpoint_id, role_doc)
    formatted_print(res, simple_text="ID: {}".format(res["id"]))
