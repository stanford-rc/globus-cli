.. globus-cli examples master file

Globus CLI Examples
===================

.. note::
    The following examples are all written for a Bash shell. If you are running
    another shell you may need to modify the non globus commands and syntax
    found in these examples.

    These examples also assume the user has already successfully logged into
    Globus. To do so run

    .. code-block:: bash

        $ globus login

    and follow the instructions.
    If you are having problems logging in, consult
    :ref:`Getting Started <getting_started>`


Finding an Endpoint
-------------------

Searches for a tutorial endpoint, then stores its ID in a local variable to
allow for human-readable calls to further globus endpoint commands.

.. code-block:: bash

    $ globus endpoint search "Globus Tutorial Endpoint"
    Owner                      | ID                                   | Display Name
    -------------------------- | ------------------------------------ | --------------------------
    go@globusid.org            | ddb59aef-6d04-11e5-ba46-22000b92c6ec | Globus Tutorial Endpoint 1
    go@globusid.org            | ddb59af0-6d04-11e5-ba46-22000b92c6ec | Globus Tutorial Endpoint 2

    # copy and paste the desired Endpoint ID from the search results
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec

    # now we can use the endpoint in a human readable fashion
    $ globus endpoint show $ep1
    Display Name:              Globus Tutorial Endpoint 1
    ID:                        ddb59aef-6d04-11e5-ba46-22000b92c6ec
    Owner:                     go@globusid.org
    Activated:                 True
    Shareable:                 True
    Department:                None
    Keywords:                  None
    Endpoint Info Link:        None
    Contact E-mail:            None
    Organization:              None
    Department:                None
    Other Contact Info:        None
    Visibility:                True
    Default Directory:         None
    Force Encryption:          False
    Managed Endpoint:          True
    Subscription ID:           964be8f5-5f9b-11e4-b64e-12313940394d
    Legacy Name:               go#ep1
    Local User Info Available: False


Search results truncated for readability.


Endpoint Manipulation
---------------------

Demonstrates the synchronous commands of mkdir, rename, and ls.

.. code-block:: bash

    # Tutorial Endpoint ID found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec

    # Make a new directory
    $ globus mkdir $ep1:~/cli_example_dir
    The directory was created successfully

    # Rename the directory
    $ globus rename $ep1:~/cli_example_dir $ep1:~/cli_example_dir_renamed
    File or directory renamed successfully

    # Show the directory contents after the changes
    # (assuming ~/ was empty before these commands)
    $ globus ls $ep1:~/
    cli_example_dir_renamed/


Single Item Transfers
---------------------

Submits transfer requests for a file and a directory from one Globus Tutorial
Endpoint to another

.. code-block:: bash

    # Tutorial Endpoint IDs found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec
    $ ep2=ddb59af0-6d04-11e5-ba46-22000b92c6ec

    # transfer file1.txt from one endpoint to another
    $ globus transfer $ep1:/share/godata/file1.txt $ep2:~/file1.txt \
        --label "CLI single file"
    Message: The transfer has been accepted and a task has been created and queued for execution
    Task ID: 466a5962-dda0-11e6-9d11-22000a1e3b52

    # recursively transfer the godata folder from one endpoint to another
    $ globus transfer $ep1:/share/godata $ep2:~/godata \
        --recursive --label "CLI single folder"
    Message: The transfer has been accepted and a task has been created and queued for execution
    Task ID: 47477b62-dda0-11e6-9d11-22000a1e3b52


Batch Transfers
---------------

Uses a .txt file to request multiple files in one transfer request.

.. code-block:: bash

    # this is the contents of in.txt:
    # a list of source paths followed by destination paths

    file1.txt file1.txt
    file2.txt file2.txt # inline-comments are also allowed
    file3.txt file3.txt

.. code-block:: bash

    # Tutorial Endpoint IDs found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec
    $ ep2=ddb59af0-6d04-11e5-ba46-22000b92c6ec

    # since batch mode reads from stdin, we can direct input from a .txt file
    # all paths from stdin are relative to the paths supplied here
    $ globus transfer $ep1:/share/godata/ $ep2:~/ \
        --batch --label "CLI Batch" < in.txt
    Message: The transfer has been accepted and a task has been created and queued for execution
    Task ID: 306900e0-dda1-11e6-9d11-22000a1e3b52

Note that only one task was needed even though there are multiple files to be
transferred.


Deletions
---------

Submits delete task requests for the files transferred by the previous two
examples. Note that even if the target files are non-existent this example will
still submit delete tasks without error, but the tasks themselves will fail.

.. code-block:: bash

    # this is the contents of in.txt:
    # a list of source paths

    file1.txt
    file2.txt # inline comments are supported
    file3.txt

.. code-block:: bash

    # Tutorial Endpoint ID found from 'globus endpoint search Tutorial'
    $ ep2=ddb59af0-6d04-11e5-ba46-22000b92c6ec

    # recursive deletion of a single folder
    $ globus delete $ep2:~/godata --recursive --label "CLI single delete"
    Message: The delete has been accepted and a task has been created and queued for execution
    Task ID: a3ec193a-dda1-11e6-9d11-22000a1e3b52

    # batch deletion of multiple files
    # we are again using a .txt file for our batch stdin
    $ globus delete $ep2:~/ --batch --label "CLI batch delete" < in.txt
    Message: The delete has been accepted and a task has been created and queued for execution
    Task ID: a4761f4a-dda1-11e6-9d11-22000a1e3b52


Task Management
---------------

Submits an unauthorized transfer task to demonstrate how to view data
on why a task hasn't completed and then cancel the task

.. code-block:: bash

    # Tutorial Endpoint IDs found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec
    $ ep2=ddb59af0-6d04-11e5-ba46-22000b92c6ec

    # submit a transfer request we do not have permission for
    $ globus transfer $ep1:/share/godata $ep2:/share/godata \
        --recursive --label "Unauthorized Transfer"
    Message: The transfer has been accepted and a task has been created and queued for execution
    Task ID: 67d6e4ba-dda2-11e6-9d11-22000a1e3b52

    # copy and paste the task id for later use
    $ task_id=67d6e4ba-dda2-11e6-9d11-22000a1e3b52

    # view details about the task
    # note the Details field reads PERMISSION_DENIED
    $ globus task show $task_id
    Label:                Unauthorized Transfer
    Task ID:              67d6e4ba-dda2-11e6-9d11-22000a1e3b52
    Type:                 TRANSFER
    Directories:          1
    Files:                3
    Status:               ACTIVE
    Request Time:         2017-01-18 17:20:28+00:00
    Deadline:             2017-01-19 17:20:28+00:00
    Details:              PERMISSION_DENIED
    Source Endpoint:      Globus Tutorial Endpoint 1
    Destination Endpoint: Globus Tutorial Endpoint 2

    # cancel the task
    $ globus task cancel $task_id
    The task has been cancelled successfully.

Note the Details field read PERMISSION_DENIED, but the status field was still
ACTIVE. Globus will eventually time out such a request when the Deadline is
reached, but the user has until then to try to repair any permissions.


Bookmarks
---------

Creates a bookmark then demonstrates how they can be used in place of UUIDs

.. code-block:: bash

    # Tutorial Endpoint ID found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec

    # Make a new bookmark at Tutorial Endpoint 1's godata folder
    $ globus bookmark create $ep1:/share/godata/ "Example Bookmark"
    Bookmark ID: ab45785a-dda3-11e6-9d11-22000a1e3b52

    # The bookmark now shows up in the bookmarks list
    $ globus bookmark list
    Name             | Endpoint ID                          | Bookmark ID                          | Path
    ---------------- | ------------------------------------ | ------------------------------------ | --------------
    Example Bookmark | ddb59aef-6d04-11e5-ba46-22000b92c6ec | ab45785a-dda3-11e6-9d11-22000a1e3b52 | /share/godata/

    # The bookmark can now be used to get a path without any UUIDs
    $ globus ls $(globus bookmark show "Example Bookmark")
    file1.txt
    file2.txt
    file3.txt


Shared Endpoints
----------------

Makes a directory on a Tutorial Endpoint, sets it up as a Shared Endpoint, and
creates a permission for that endpoint.

.. code-block:: bash

    # Tutorial Endpoint ID found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec

    # set up a directory to be our shared endpoint
    # note that this will throw an error if a directory already exists at this path
    $ globus mkdir $ep1:~/shared_dir
    The directory was created successfully

    # set up the directory as a shared endpoint
    $ globus endpoint create --shared $ep1:/~/shared_dir "CLI Example Shared Endpoint" \
        --description "Example endpoint created using the Globus CLI"
    Message:     Shared endpoint created successfully
    Endpoint ID: 3e4efafe-dda4-11e6-9d11-22000a1e3b52

    # copy and paste the new shared endpoint ID for later use
    $ shared=<paste here>

    # add a permission to the endpoint
    # this permission is r for read only
    # and is given to anyone who has logged in
    $ globus endpoint permission create $shared:/ \
        --permissions r --all-authenticated
    Message: Access rule created successfully.
    Rule ID: 62f909c6-dda4-11e6-9d11-22000a1e3b52

    # the new permission will now appear on the endpoints permission list
    # note that the new permission appears alongside the owner's automatic
    # read-write permissions
    $ globus endpoint permission list $shared
    Rule ID                              | Permissions | Shared With             | Path
    ------------------------------------ | ----------- | ----------------------- | ----
    62f909c6-dda4-11e6-9d11-22000a1e3b52 | r           | all_authenticated_users | /
    NULL                                 | rw          | example@globusid.org    | /

    # the endpoint itself also shows up on your list of shared endpoints
    $ globus endpoint search --filter-scope shared-by-me
    Owner                 | ID                                   | Display Name
    --------------------- | ------------------------------------ | ---------------------------
    example@globusid.org  | 3e4efafe-dda4-11e6-9d11-22000a1e3b52 | CLI Example Shared Endpoint




Safe Resubmissions
------------------

Generates a submission-id that allows for resubmitting a task multiple times
while guaranteeing that the actual task will only be carried out once.
This is useful for handling the unreliability of networks.

Note that the task ID of the task will differ from the submission ID.

.. code-block:: bash

    # Tutorial Endpoint IDs found from 'globus endpoint search Tutorial'
    $ ep1=ddb59aef-6d04-11e5-ba46-22000b92c6ec
    $ ep2=ddb59af0-6d04-11e5-ba46-22000b92c6ec

    # generate and store a UUID for the submission-id
    $ sub_id=$(globus task generate-submission-id)

    # submit multiple transfers using the same submission-id
    $ globus transfer $ep1:/share/godata $ep2:~/godata --recursive \
        --submission-id $sub_id --label "1st submission"
    Message: The transfer has been accepted and a task has been created and queued for execution
    Task ID: 8b43c4e2-dda5-11e6-9d11-22000a1e3b52

    $ globus transfer $ep1:/share/godata $ep2:~/godata --recursive \
        --submission-id $sub_id --label "2nd submission"
    Message: A transfer with id '8b43c4e3-dda5-11e6-9d11-22000a1e3b52' was already submitted
    Task ID: 8b43c4e2-dda5-11e6-9d11-22000a1e3b52

    $ globus transfer $ep1:/share/godata $ep2:~/godata --recursive \
        --submission-id $sub_id --label "3rd submission"
    Message: A transfer with id '8b43c4e3-dda5-11e6-9d11-22000a1e3b52' was already submitted
    Task ID: 8b43c4e2-dda5-11e6-9d11-22000a1e3b52

    # view the task list to confirm only one task was submitted
    $ globus task list
    Task ID                              | Status    | Type     | Source Display Name        | Dest Display Name          | Label
    ------------------------------------ | --------- | -------- | -------------------------- | -------------------------- | ---------------------
    8b43c4e2-dda5-11e6-9d11-22000a1e3b52 | SUCCEEDED | TRANSFER | Globus Tutorial Endpoint 1 | Globus Tutorial Endpoint 2 | 1st submission

Note that only one submission has a success message, but all return the ID for
the Task, which only gets carried out once.
