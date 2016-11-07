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
submission_doc=$(
    globus transfer --batch --dry-run \
        --submission-id '89330878-9ffe-11e6-b61b-8c705ad34f60' \
        'ddb59aef-6d04-11e5-ba46-22000b92c6ec' \
        'ddb59af0-6d04-11e5-ba46-22000b92c6ec:base/' \
    << EOF
        abc /def
        /xyz p/q/r
EOF
)
fgrep '"source_path": "abc"' <<< $submission_doc
fgrep '"destination_path": "/def"' <<< $submission_doc
fgrep '"source_path": "/xyz"' <<< $submission_doc
fgrep '"destination_path": "base/p/q/r"' <<< $submission_doc
