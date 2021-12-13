### Enhancements

* Add support for client credentials for authentication in the Globus CLI
  by setting GLOBUS_CLI_CLIENT_ID and GLOBUS_CLI_CLIENT_SECRET
  environment variables (:pr:`NUMBER`)
** Both variables must be set to enable this behavior
** Tokens generated with client credentials are cached in the current user's home
   directory, but isolated from any user credentials
** With client credentials, `globus login` is invalid, but `globus logout` can be used
   to revoke any cached tokens
