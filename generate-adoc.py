#!/usr/bin/env python3
"""manpage-like asciidoc generator for CLI web pages

based heavily on click-man
"""
import os
import time

import click
from pkg_resources import load_entry_point

version_ns = {}
with open(os.path.join("globus_cli", "version.py")) as f:
    exec(f.read(), version_ns)
VERSION = version_ns["__version__"]

CLI = load_entry_point("globus-cli", "console_scripts", "globus")

HERE = os.path.dirname(__file__)
TARGET_DIR = os.path.join(HERE, "adoc")

DATE = time.strftime("%Y-%m-%d", time.gmtime())


def _format_option(optstr):
    opt = optstr.split()
    optnames, optparams = [], []
    for o in opt:
        if not optparams and o.startswith("-"):
            optnames.append(o)
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
        self.description = ctx.command.help
        self.synopsis = _format_synopsis(ctx.command.collect_usage_pieces(ctx))
        self.options = [
            y
            for y in [
                x.get_help_record(ctx)
                for x in ctx.command.params
                if isinstance(x, click.Option)
            ]
            if y
        ]

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
            )

        return "\n".join(sections)


def render_page(ctx):
    return str(AdocPage(ctx))


def write_pages(name, cmd, parent_ctx=None):
    ctx = click.Context(cmd, info_name=name, parent=parent_ctx)

    if not isinstance(cmd, click.Group):
        cmd_name = ctx.command_path.replace(" ", "-")
        cmd_name = cmd_name[len("globus-") :]
        path = os.path.join(TARGET_DIR, cmd_name + ".adoc")
        print(f"rendering {name} to {path}")

        with open(path, "w") as f:
            f.write(render_page(ctx))

    for subcmdname, subcmd in getattr(cmd, "commands", {}).items():
        if subcmd.hidden:
            continue
        write_pages(subcmdname, subcmd, parent_ctx=ctx)


if __name__ == "__main__":
    write_pages("globus", CLI)
