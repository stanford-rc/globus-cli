.. globus-cli documentation master file

Globus CLI
==========

.. warning::
    This page refers to the beta version of the new Globus CLI, which is an
    application you download and locally install.
    Please try out the new CLI, and send us your feedback at support@globus.org

    This CLI is still in beta and updates and changes to the interfaces are
    expected as newer versions are released.

    If you are looking for the current CLI available in production please see
    https://docs.globus.org/cli

This CLI provides a convenient shell interface to
`Globus <https://www.globus.org>`_ APIs,
including the Transfer API and the Globus Auth API.

Documentation for the APIs is available at https://docs.globus.org

You can always view CLI help by passing the `--help` flag to a command. That
will show you any subcommands and options supported by that command.

Source code is available at https://github.com/globus/globus-cli

Installation
============

The Globus CLI is maintained as a python package, built on the
`Globus Python SDK <https://globus.github.io/globus-sdk-python>`_.
Like the SDK, it therefore requires `Python <https://www.python.org/>`_ 2.7+ or
3.3+.
If a supported version of Python is not already installed on your system, see
this `Python installation guide\
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

.. rubric:: For macOS Users

For **macOS**, you must install pip first:

.. code-block:: bash

    which pip || sudo easy_install pip

.. rubric:: For All Platforms

To install, run the following commands:

.. _install_script:

.. code-block:: bash

    which virtualenv || sudo pip install virtualenv
    virtualenv "$HOME/.globus-cli-virtualenv"
    source "$HOME/.globus-cli-virtualenv/bin/activate"
    pip install globus-cli
    deactivate
    export PATH="$PATH:$HOME/.globus-cli-virtualenv/bin"
    echo 'export PATH="$PATH:$HOME/.globus-cli-virtualenv/bin"' >> "$HOME/.bashrc"

This will install the CLI and its dependencies into
``$HOME/.globus-cli-virtualenv``, and add it to your shell.

See that the CLI is installed:

.. code-block:: bash

    globus --help

.. rubric:: Note on Other Shells

If you shell is not Bash, you will have to add
``export PATH="$PATH:$HOME/.globus-cli-virtualenv/bin"`` to your shell's
initialization file.

.. rubric:: Updating and Removing

For more info, see the instructions on :ref:`Updating and Removing CLI
Versions <updating_and_removing>`.


Getting Started
===============

Installing the ``globus-cli`` python packge will provide you with the
``globus`` command.
However, most CLI commands will require authentication to Globus services, so
start out by getting logged in:

.. code-block:: bash

    $ globus login
    # follow instructions to get setup

You can check that you can correctly authenticate to the Globus APIs with two
quick commands.

First, check that you can access Globus Auth:

.. code-block:: bash

    $ globus get-identities 'go@globusid.org'
    ID                                   | Full Name      | Username        | Organization | Email Address
    ------------------------------------ | -------------- | --------------- | ------------ | ------------------
    c699d42e-d274-11e5-bf75-1fc5bf53bb24 | www.globus.org | go@globusid.org | Globus       | noreply@globus.org

Your output should be the same as above.
If you are not authenticated, you will see a message similar to:

.. code-block:: bash

    $ globus get-identities 'go@globusid.org'
    Globus CLI Error: A GLobus API Error Occurred.
    HTTP status:      401
    code:             UNAUTHORIZED
    message:          Call must be authenticated

Next, check that you can reach the Globus Transfer API:

.. code-block:: bash

    # --filter-owner-id is the ID of 'go@globusid.org', fetched above
    $ globus endpoint search 'Globus Tutorial Endpoint' \
        --filter-owner-id 'c699d42e-d274-11e5-bf75-1fc5bf53bb24'
    Owner           | ID                                   | Display Name
    --------------- | ------------------------------------ | ---------------------------
    go@globusid.org | ddb59aef-6d04-11e5-ba46-22000b92c6ec | Globus Tutorial Endpoint 1
    go@globusid.org | ddb59af0-6d04-11e5-ba46-22000b92c6ec | Globus Tutorial Endpoint 2
    go@globusid.org | cf9bcaa5-6d04-11e5-ba46-22000b92c6ec | Globus S3 Tutorial Endpoint

If you are not authenticated, you will get an error like the following:

.. code-block:: bash

    $ globus endpoint search 'Globus Tutorial Endpoint' \
        --filter-owner-id 'c699d42e-d274-11e5-bf75-1fc5bf53bb24'
    Globus CLI Error: A Transfer API Error Occurred.
    HTTP status:      401
    request_id:       1AghTj1F6
    code:             AuthenticationFailed
    message:          Token is not active

Now we have the endpoint IDs for the tutorial endpoints, and can do a test
directory listing:

.. code-block:: bash

    $ globus ls 'ddb59aef-6d04-11e5-ba46-22000b92c6ec:/'
    home
    mnt
    not shareable
    share

Start exploring the CLI!

Use ``globus list-commands`` to see all of the commands in the CLI, and to get
more detailed help for a specific information on a command, run that command
with the ``--help`` flag.

.. _updating_and_removing:

Updating & Removing the CLI
===========================

Update
------

To update your version of the CLI to the latest:

.. code-block:: bash

    source "$HOME/.globus-cli-virtualenv/bin/activate"
    pip install -U globus-cli
    deactivate

Uninstall
---------

To remove the CLI:

.. code-block:: bash

    rm -r "$HOME/.globus-cli-virtualenv"

You should also edit your ``$HOME/.bashrc`` and remove the line that reads
``export PATH="$PATH:$HOME/.globus-cli-virtualenv/bin"``.

License
=======

Copyright 2016 University of Chicago

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
