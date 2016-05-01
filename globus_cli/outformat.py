import click

from globus_cli.helpers import JSON_FORMAT, TEXT_FORMAT


class OutFormat(click.Choice):
    name = 'format'

    def __init__(self):
        click.Choice.__init__(self, [JSON_FORMAT, TEXT_FORMAT])

    def convert(self, value, param, ctx):
        if value is None:
            return None

        s = value.lower()
        if s == 'json':
            return JSON_FORMAT
        elif s == 'text':
            return TEXT_FORMAT
        else:
            ValueError('Invalid Output Format Specified')
