.. globus-cli documentation master file

Globus CLI
==========

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
Like the SDK, it therefore requires `Python <https://www.python.org/>`_ 2.6+ or
3.2+.
If a supported version of Python is not already installed on your system, see
this `Python installation guide \
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

The simplest way to install the Globus CLI is using the ``pip`` package manager
(https://pypi.python.org/pypi/pip), which is included in most Python
installations:

.. code-block:: bash

    pip install globus-cli

This will install the CLI and it's dependencies.

Bleeding edge versions of the Globus SDK can be installed by checking out the
git repository and installing it manually:

.. code-block:: bash

    git checkout https://github.com/globus/globus-cli.git
    cd globus-cli
    python setup.py install


Getting Started
===============

Installing the ``globus-cli`` python packge will provide you with the
``globus`` command.
However, most CLI commands will require authentication to Globus services, so
start out by getting tokens:

.. code-block:: bash

    $ globus login
    # follow instructions to get setup

You can check that you can correctly authenticate to the Globus APIs with two
quick commands.

First, check that you can access Globus Auth:

.. code-block:: bash

    $ globus auth get-identities --usernames 'go@globusid.org'
    {
      "identities": [
        {
          "username": "go@globusid.org", 
          "status": "used", 
          "name": "www.globus.org", 
          "id": "c699d42e-d274-11e5-bf75-1fc5bf53bb24", 
          "identity_provider": "41143743-f3c8-4d60-bbdb-eeecaba85bd9", 
          "organization": "Globus", 
          "email": "noreply@globus.org"
        }
      ]
    }

Your output should be the same as above.
If you are not authenticated, you will see a message similar to:

.. code-block:: bash

    $ globus auth get-identities --usernames 'go@globusid.org'
    Globus CLI Error: A Globus API Error Occurred.
    HTTP status: 401
    code: UNAUTHORIZED
    message: Call must be authenticated

Next, check that you can reach the Globus Transfer API:

.. code-block:: bash

    # --filter-owner-id is the ID of 'go@globusid.org', fetched above
    $ globus transfer endpoint search \
        --filter-fulltext 'Globus Tutorial Endpoint' \
        --filter-owner-id 'c699d42e-d274-11e5-bf75-1fc5bf53bb24'  
    Owner                            | ID                                   | Display Name
    -------------------------------- | ------------------------------------ | ------------
    go@globusid.org                  | ddb59aef-6d04-11e5-ba46-22000b92c6ec | Globus Tutorial Endpoint 1
    go@globusid.org                  | ddb59af0-6d04-11e5-ba46-22000b92c6ec | Globus Tutorial Endpoint 2
    go@globusid.org                  | cf9bcaa5-6d04-11e5-ba46-22000b92c6ec | Globus S3 Tutorial Endpoint

If you are not authenticated, you will get an error like the following:

.. code-block:: bash

    $ globus transfer endpoint search \
        --filter-fulltext 'Globus Tutorial Endpoint' \
        --filter-owner-id 'c699d42e-d274-11e5-bf75-1fc5bf53bb24'  
    Globus CLI Error: A Transfer API Error Occurred.
    request_id: I33fDzZPp
    code: AuthenticationFailed
    message: Token is not active

Now we have the endpoint IDs for the tutorial endpoints, and can do a test
directory listing:

.. code-block:: bash

    $ globus transfer ls \
        --endpoint-id 'ddb59aef-6d04-11e5-ba46-22000b92c6ec' \
        --path '/'
    home
    mnt
    not shareable
    share

Start exploring the CLI!
Use ``globus list-commands`` to see all of the commands in the CLI, and to get
more detailed help for a specific information on a command, run that command
with the ``--help`` flag.

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
