### Bugfixes

* `globus session consent` was reducing the scopes of the Auth token provided
  by login, resulting in errors on `logout` and `whoami`
