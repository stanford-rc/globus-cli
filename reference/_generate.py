#!/usr/bin/env python3
"""asciidoc generator for CLI web pages

based originally on click-man, but significantly specialized for the globus-cli
"""
import os
import time

import click
import requests
from pkg_resources import load_entry_point

version_ns = {}
with open(os.path.join("globus_cli", "version.py")) as f:
    exec(f.read(), version_ns)
VERSION = version_ns["__version__"]

CLI = load_entry_point("globus-cli", "console_scripts", "globus")

TARGET_DIR = os.path.dirname(__file__)

try:
    # try to fetch last release date
    last_release = requests.get(
        "https://api.github.com/repos/globus/globus-cli/releases/latest"
    )
    REV_DATE = time.strptime(last_release.json()["published_at"], "%Y-%m-%dT%H:%M:%SZ")
except Exception:
    # fallback to current time
    REV_DATE = time.gmtime()
REV_DATE = time.strftime("%B %d, %Y", REV_DATE)


EXIT_STATUS_TEXT = """0 on success.

1 if a network or server error occurred, unless --map-http-status has been
used to change exit behavior on http error codes.

2 if the command was used improperly.
"""
EXIT_STATUS_NOHTTP_TEXT = """0 on success.

1 if an error occurred

2 if the command was used improperly.
"""


def _format_option(optstr):
    opt = optstr.split()
    optnames, optparams = [], []
    slashopt = False
    for o in opt:
        if slashopt:
            slashopt = False
            optnames[-1] = optnames[-1] + " / " + o
            continue
        if not optparams:
            if o.startswith("-"):
                optnames.append(o)
                continue
            elif o == "/":
                slashopt = True
                continue
        optparams.append(o)
    optnames = " ".join(optnames)

    optnames = f"*{optnames}*"
    optparams = [f"'{x}'" for x in optparams]
    if optparams:
        optparams = " " + " ".join(optparams)
    else:
        optparams = ""

    return f"{optnames}{optparams}::"


def _format_multiline_str(s):
    return s.replace("\n\n", "\n+\n")


def _format_synopsis(usage_pieces):
    as_str = " ".join(usage_pieces)
    if as_str.endswith("..."):
        as_str = as_str[:-3]
    return as_str


class AdocPage:
    def __init__(self, ctx):
        self.commandname = ctx.command_path
        self.short_help = ctx.command.get_short_help_str()
        self.description = ctx.command.help.replace("\b\n", "")
        self.synopsis = ctx.command.adoc_synopsis or _format_synopsis(
            ctx.command.collect_usage_pieces(ctx)
        )
        self.options = [
            y
            for y in [
                x.get_help_record(ctx)
                for x in ctx.command.params
                if isinstance(x, click.Option)
            ]
            if y
        ]
        self.output = ctx.command.adoc_output
        self.examples = ctx.command.adoc_examples
        uses_http = "map_http_status" not in ctx.command.globus_disable_opts
        self.exit_status_text = ctx.command.adoc_exit_status or (
            EXIT_STATUS_TEXT if uses_http else EXIT_STATUS_NOHTTP_TEXT
        )

    def __str__(self):
        sections = []
        sections.append(f"= {self.commandname.upper()}\n")

        sections.append(
            f"""== NAME

{self.commandname} - {self.short_help}
"""
        )
        sections.append(
            f"""== SYNOPSIS

`{self.commandname} {self.synopsis}`
"""
        )
        if self.description:
            sections.append(
                f"""== DESCRIPTION

{self.description}
"""
            )
        if self.options:
            sections.append(
                "== OPTIONS\n"
                + "\n".join(
                    "\n" + _format_option(opt) + "\n\n" + _format_multiline_str(desc)
                    for opt, desc in self.options
                )
                + "\n"
            )

        if self.output:
            sections.append(
                f"""== OUTPUT

{self.output}"""
            )
            if not self.output.endswith("\n"):
                sections.append("")
        if self.examples:
            sections.append(
                f"""== EXAMPLES

{self.examples}"""
            )
            if not self.examples.endswith("\n"):
                sections.append("")

        sections.append(
            f"""== EXIT STATUS

{self.exit_status_text}"""
        )
        if not self.exit_status_text.endswith("\n"):
            sections.append("")

        return "\n".join(sections)


def render_page(ctx):
    return str(AdocPage(ctx))


def write_pages(name, cmd, parent_ctx=None):
    ctx = click.Context(cmd, info_name=name, parent=parent_ctx)

    if not isinstance(cmd, click.Group) and not getattr(cmd, "adoc_skip", True):
        cmd_name = ctx.command_path.replace(" ", "_")
        cmd_name = cmd_name[len("globus_") :]
        path = os.path.join(TARGET_DIR, cmd_name + ".adoc")
        print(f"rendering {name} to {path}")

        with open(path, "w") as f:
            f.write(render_page(ctx))

    for subcmdname, subcmd in getattr(cmd, "commands", {}).items():
        if subcmd.hidden:
            continue
        write_pages(subcmdname, subcmd, parent_ctx=ctx)


class CmdForIndex:
    def __init__(self, name, cmd, parent_ctx):
        ctx = click.Context(cmd, info_name=name, parent=parent_ctx)
        self.name = name
        self.link = name.replace(" ", "_")[len("globus_") :]
        self.summary = ctx.command.get_short_help_str()


def collect_commands(heading, name, cmd, parent_ctx=None):
    ctx = click.Context(cmd, info_name=name, parent=parent_ctx)
    subcommands = []
    sub_groups = []
    for subcmdname, subcmd in getattr(cmd, "commands", {}).items():
        fullname = name + " " + subcmdname
        # explicitly skip hiden commands and `globus config`
        if subcmd.hidden or fullname == "globus config":
            continue
        if isinstance(subcmd, click.Group):
            sub_groups.append((fullname, subcmd))
        else:
            subcommands.append(CmdForIndex(fullname, subcmd, ctx))

    if subcommands:
        yield heading, subcommands

    for groupname, group in sub_groups:
        for subheading, subcommands in collect_commands(
            f"== {groupname} commands", groupname, group
        ):
            yield subheading, subcommands


def generate_index():
    with open(os.path.join(TARGET_DIR, "index.adoc"), "w") as f:
        # header required for globus docs to specify extra attributes
        f.write(
            """---
menu_weight: 10
short_title: Reference
---
"""
        )
        for heading, commands in collect_commands(
            f"""= Command Line Interface (CLI) Reference

[doc-info]*Last Updated: {REV_DATE}*""",
            "globus",
            CLI,
        ):
            f.write(heading + "\n\n")
            for cmd in commands:
                f.write(f"link:{cmd.link}[{cmd.name}]::\n")
                f.write(cmd.summary + "\n\n")


if __name__ == "__main__":
    write_pages("globus", CLI)
    generate_index()
