# single source of truth for package version,
# see https://packaging.python.org/en/latest/single_source_version/


# The Globus CLI version *always* starts with the version of the SDK which it
# depends upon. If necessary, we do additional point releases upon the SDK
# version.
# For example, if the SDK version is
#       2.4.6
# then the following are valid CLI versions:
#       2.4.6.0
#       2.4.6.1
#       2.4.6.10
#       2.4.6.99
# and the following invalid CLI versions:
#       2.4.6       -- doesn't specify point release
#       2.4.7.0     -- should depend on SDK 2.4.7
#       2.4.6.1.2   -- no additional point versions
#       0.1.0.0     -- no special rules for things like this
#       1.4.6.0     -- differing major version, obviously wrong
__version__ = "0.4.0.0"

# app name to send as part of SDK requests
app_name = 'Globus CLI v{} - Alpha'.format(__version__)
