import click

from globus_cli.safeio import safeprint
from globus_cli.version import get_versions


def version_option(f):
    """
    Largely a custom clone of click.version_option -- almost identical, but
    makes more assumptions and prints our special output.
    """
    def callback(ctx, param, value):
        # copied from click.decorators.version_option
        # no idea what resilient_parsing means, but...
        if not value or ctx.resilient_parsing:
            return

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
                    ('You should update your version of the Globus CLI\n'
                     'Update instructions: '
                     'https://globus.github.io/globus-cli/'
                     '#updating-and-removing')
                     if current < latest else
                     'You are running a preview version of the Globus CLI'
                )
            )

        ctx.exit(0)

    return click.option('--version', help='Show the version and exit.',
                        is_flag=True, expose_value=False, is_eager=True,
                        callback=callback)(f)
