from distutils.version import LooseVersion

# single source of truth for package version,
# see https://packaging.python.org/en/latest/single_source_version/
__version__ = "1.16.0"

# app name to send as part of SDK requests
app_name = f"Globus CLI v{__version__}"


# pull down version data from PyPi
def get_versions():
    """
    Wrap in a function to ensure that we don't run this every time a CLI
    command runs (yuck!)

    Also protects import of `requests` from issues when grabbed by setuptools.
    More on that inline

    Returns a 3-tuple:
      (upgrade_target, latest_version, current_version)

    For CLI v1.x, upgrade_target is the latest v1 version IF you are on a python2
    interpreter.
    latest_version is the unbounded most recent version (could be 2.x, 3.x, etc)
    regardless of runtime.
    """
    # import in the func (rather than top-level scope) so that at setup time,
    # `requests` and `six` aren't required -- otherwise, setuptools will fail to run
    # because they aren't installed yet.
    import requests
    import six

    try:
        version_data = requests.get(
            "https://pypi.python.org/pypi/globus-cli/json"
        ).json()
        parsed_versions = [LooseVersion(v) for v in version_data["releases"]]
        upgrade_target = latest = max(parsed_versions)
        # python2 only; limit the upgrade to only the latest v1
        if six.PY2:
            upgrade_target = max(
                v for v in parsed_versions if v < LooseVersion("2.0.0")
            )
        return upgrade_target, latest, LooseVersion(__version__)
    # if the fetch from pypi fails
    except requests.RequestException:
        return None, None, LooseVersion(__version__)
