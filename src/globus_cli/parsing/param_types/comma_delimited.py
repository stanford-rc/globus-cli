import click


class CommaDelimitedList(click.ParamType):
    def get_metavar(self, param):
        return "TEXT,TEXT,..."

    def convert(self, value, param, ctx):
        value = super().convert(value, param, ctx)
        if value is None:
            return None
        # if `--foo` is a comma delimited list and someone passes
        # `--foo ""`, take that as `foo=[]` rather than foo=[""]
        #
        # the alternative is fine, but we have to choose one and this is
        # probably "closer to what the caller meant"
        #
        # it means that if you take
        # `--foo={",".join(original)}`, you will get a value equal to
        # `original` back if `original=[]` (but not if `original=[""]`)
        elif value == "":
            return []
        else:
            return value.split(",")
