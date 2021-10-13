### Bugfixes

* Fix the handling of the legacy-line of `virtualenv`, versions below `20.0.0`.
  When the `globus-cli` was installed under these versions of `virtualenv`, all
  commands would fail at import-time due to an API difference between stdlib
  `site` module and the `virtualenv`-generated `site`
