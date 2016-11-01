#!/bin/bash

# poor man's testsuite: run a bunch of commands and confirm that they don't
# crash and burn catastrophically
set -e

# parsing failures
globus --help
# actually running a command
globus list-commands
# auth call (noauth)
globus get-identities 'abc@globus.org' --map-http-status "401=0"
# transfer call (noauth)
globus ls 'ddb59aef-6d04-11e5-ba46-22000b92c6ec' --map-http-status "400=0"

# transfer batchmode dry-run
echo -e "abc /def\n/xyz p/q/r" | \
    globus transfer --batch --dry-run \
        --submission-id '89330878-9ffe-11e6-b61b-8c705ad34f60' \
        'ddb59aef-6d04-11e5-ba46-22000b92c6ec' \
        'ddb59af0-6d04-11e5-ba46-22000b92c6ec:base/' | \
    tr '\n' ' ' | \
    egrep '"destination_path": "/def".*"source_path": "abc".*"destination_path": "base/p/q/r".*"source_path": "/xyz"'
