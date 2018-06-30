import platform
import site
import sys

from globus_cli.helpers.options import is_verbose, verbosity
from globus_cli.safeio import safeprint
from globus_cli.version import get_versions


def _get_package_data():
    """
    Import a set of important packages and return relevant data about them in a
    dict.
    Imports are done in here to avoid potential for circular imports and other
    problems, and to make iteration simpler.
    """
    moddata = []
    modlist = ('click', 'configobj', 'cryptography', 'globus_cli',
               'globus_sdk', 'jmespath', 'requests', 'six')
    if verbosity() < 2:
        modlist = ('globus_cli', 'globus_sdk', 'requests')

    for mod in modlist:
        cur = [mod]
        try:
            loaded_mod = __import__(mod)
        except ImportError:
            loaded_mod = None

        for attr in ('__version__', '__file__', '__path__'):
            # if loading failed, be sure to pad with error messages
            if loaded_mod is None:
                cur.append('[import failed]')
                continue

            try:
                attrval = getattr(loaded_mod, attr)
            except AttributeError:
                attrval = ''
            cur.append(attrval)
        moddata.append(cur)

    return moddata


def print_version():
    """
    Print out the current version, and at least try to fetch the latest from
    PyPi to print alongside it.

    It may seem odd that this isn't in globus_cli.version , but it's done this
    way to separate concerns over printing the version from looking it up.
    """
    latest, current = get_versions()
    if latest is None:
        safeprint(('Installed Version: {0}\n'
                   'Failed to lookup latest version.')
                  .format(current))
    else:
        safeprint(
            ('Installed Version: {0}\n'
             'Latest Version:    {1}\n'
             '\n{2}').format(
                current, latest,
                'You are running the latest version of the Globus CLI'
                if current == latest else
                ('You should update your version of the Globus CLI with\n'
                 '  globus update')
                 if current < latest else
                 'You are running a preview version of the Globus CLI'
            )
        )

    # verbose shows more platform and python info
    # it also includes versions of some CLI dependencies
    if is_verbose():
        moddata = _get_package_data()

        safeprint('\nVerbose Data\n---')

        safeprint('platform:')
        safeprint('  platform: {}'.format(platform.platform()))
        safeprint('  py_implementation: {}'
                  .format(platform.python_implementation()))
        safeprint('  py_version: {}'.format(platform.python_version()))
        safeprint('  sys.executable: {}'.format(sys.executable))
        safeprint('  site.USER_BASE: {}'.format(site.USER_BASE))

        safeprint('modules:')
        for mod, modversion, modfile, modpath in moddata:
            safeprint('  {}:'.format(mod))
            safeprint('    __version__: {}'.format(modversion))
            safeprint('    __file__: {}'.format(modfile))
            safeprint('    __path__: {}'.format(modpath))
