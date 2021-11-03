### Bugfixes

* Fix a bug in `globus session consent` in which an `id_token` was expected as
  part of the token data, but the `openid` scope was not provided to the login
  flow
