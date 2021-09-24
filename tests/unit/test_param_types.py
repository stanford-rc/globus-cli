import json

import click

from globus_cli.constants import EXPLICIT_NULL
from globus_cli.parsing import CommaDelimitedList, JSONStringOrFile, StringOrNull
from globus_cli.parsing.param_types.prefix_mapper import StringPrefixMapper


def test_string_or_null(runner):
    @click.command()
    @click.option(
        "--bar", type=StringOrNull(), default=None, help="a string or null value"
    )
    def foo(bar):
        if bar is None:
            click.echo("none")
        elif bar is EXPLICIT_NULL:
            click.echo("null")
        else:
            click.echo(bar)

    # in helptext, it shows up with "string" as the metavar
    result = runner.invoke(foo, ["--help"])
    assert "--bar TEXT  a string or null value" in result.output

    # absent, it returns None
    result = runner.invoke(foo, [])
    assert result.output == "none\n"

    # given empty string returns explicit null value
    result = runner.invoke(foo, ["--bar", ""])
    assert result.output == "null\n"

    # given a string, it returns that string
    result = runner.invoke(foo, ["--bar", "alpha"])
    assert result.output == "alpha\n"


def test_comma_delimited_list(runner):
    @click.command()
    @click.option(
        "--bar", type=CommaDelimitedList(), default=None, help="a comma delimited list"
    )
    def foo(bar):
        if bar is None:
            click.echo("nil")
        else:
            click.echo(len(bar))
            for x in bar:
                click.echo(x)

    # in helptext, it shows up with "string,string,..." as the metavar
    result = runner.invoke(foo, ["--help"])
    assert "--bar TEXT,TEXT,...  a comma delimited list" in result.output

    # absent, it returns None
    result = runner.invoke(foo, [])
    assert result.output == "nil\n"

    # given empty string (this is ambiguous!) returns empty array
    result = runner.invoke(foo, ["--bar", ""])
    assert result.output == "0\n"

    # given "alpha" it returns "['alpha']"
    result = runner.invoke(foo, ["--bar", "alpha"])
    assert result.output == "1\nalpha\n"

    # given a UUID it returns that UUID
    result = runner.invoke(foo, ["--bar", "alpha,beta"])
    assert result.output == "2\nalpha\nbeta\n"


def test_string_prefix_mapper(runner, tmpdir):
    class MyType(StringPrefixMapper):
        __prefix_mapping__ = {"bar:": "prefix_mapper_parse_bar"}
        __prefix_metavars__ = ["bar:BAR", "BAZ"]

        def prefix_mapper_parse_bar(self, value):
            if not value.startswith("BARBAR"):
                raise click.UsageError("malformed BarObject")
            return value[len("BARBAR") :]

    @click.command()
    @click.option("--bar", type=MyType(null="NIL"), default=None, help="a BarObject")
    def foo(bar):
        if bar is None:
            click.echo("nil")
        else:
            click.echo(bar)

    # in helptext, it shows up with the correct metavar
    result = runner.invoke(foo, ["--help"])
    assert "--bar [bar:BAR|BAZ]" in result.output

    # absent, it leaves the default
    result = runner.invoke(foo, [])
    assert result.output == "nil\n"

    # supports explicit null value as well
    result = runner.invoke(foo, ["--bar", "NIL"])
    assert result.output == "null\n"

    # does nothing when the value is neither the null value nor has the prefix
    result = runner.invoke(foo, ["--bar", "foo:bar"])
    assert result.output == "foo:bar\n"

    # but with the prefix, behaves as expected
    result = runner.invoke(foo, ["--bar", "bar:BARBARbaz"])
    assert result.output == "baz\n"


def test_json_string_or_file(runner, tmpdir):
    @click.command()
    @click.option("--bar", type=JSONStringOrFile(), default=None, help="a JSON blob")
    def foo(bar):
        click.echo(json.dumps(bar, sort_keys=True))

    # in helptext, it shows up with the correct metavar
    result = runner.invoke(foo, ["--help"])
    assert "--bar [JSON|file:JSON_FILE]" in result.output

    # absent, it leaves the default
    result = runner.invoke(foo, [])
    assert result.output == "null\n"

    # can be given raw json objects and parses them faithfully
    result = runner.invoke(foo, ["--bar", "null"])
    assert result.output == "null\n"
    result = runner.invoke(foo, ["--bar", '"baz"'])
    assert result.output == '"baz"\n'
    result = runner.invoke(foo, ["--bar", '{"foo": 1}'])
    assert result.output == '{"foo": 1}\n'

    # invalid JSON data causes errors
    result = runner.invoke(foo, ["--bar", '{"foo": 1,}'])
    assert result.exit_code == 2
    assert "the string '{\"foo\": 1,}' is not valid JSON" in result.output

    # something which looks like a file path but is malformed gives a specific error
    result = runner.invoke(foo, ["--bar", "file//1"])
    assert result.exit_code == 2
    assert (
        "the string 'file//1' is not valid JSON. Did you mean to use 'file:'?"
        in result.output
    )

    # given the path to a file with valid JSON, it parses the result
    valid_file = tmpdir.mkdir("valid").join("file1.json")
    valid_file.write('{"foo": 1}\n')
    result = runner.invoke(foo, ["--bar", "file:" + str(valid_file)])
    assert result.output == '{"foo": 1}\n'

    # given the path to a file with invalid JSON, it raises an error
    invalid_file = tmpdir.mkdir("invalid").join("file1.json")
    invalid_file.write('{"foo": 1,}\n')
    result = runner.invoke(foo, ["--bar", "file:" + str(invalid_file)])
    assert "did not contain valid JSON" in result.output

    # given a path to a file which does not exist, it raises an error
    missing_file = tmpdir.join("missing.json")
    result = runner.invoke(foo, ["--bar", "file:" + str(missing_file)])
    assert "FileNotFound" in result.output
    assert "does not exist" in result.output
