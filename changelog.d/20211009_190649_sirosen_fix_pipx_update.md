<!--
A new scriv changelog fragment.

Uncomment the section or sections which match your change. Use "Other" for all
changes which do not match a different section.

Fill in one or more bullet points with details of your change.

Make sure you add the new file in `changelog.d/` to your pull request!
-->

### Bugfixes

* The behavior of `globus update` when operating under a `pipx` install has
  been fixed, so that `--user` will not be passed to the `pip` invocation

### Other

* Cleanup internal and undocumented behaviors of `globus update`
