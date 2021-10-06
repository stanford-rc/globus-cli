# Changelog Dir

This is a directory of news fragment files created by `scriv`.

## Usage Guide

Install `scriv`, e.g.

    pipx install scriv

When authoring a new change, use `scriv create --edit` to write a new change document
or "newsfile".

When doing a release, _do not_ use `scriv collect`, but
`tox -e prepare-release` instead. This will run `scriv`, but also any
additional prep steps.
