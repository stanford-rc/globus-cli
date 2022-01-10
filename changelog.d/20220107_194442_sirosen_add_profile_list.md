### Enhancements

* Attempting to run `globus login` while using client credentials will show an
  appropriate error message
* A new command, `globus cli-profile-list` can be used to list values for
  `GLOBUS_PROFILE` and `GLOBUS_CLI_CLIENT_ID` ("client profiles") which have
  been used. By default, the default profile is not included in the listing and
  it is restricted to the current environment. A hidden option (`--all`) can be
  used to list all environments and include the default profiles
