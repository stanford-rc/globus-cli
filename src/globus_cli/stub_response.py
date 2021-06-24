class CLIStubResponse:
    """
    A stub response class to make arbitrary data accessible in a way similar to a
    GlobusHTTPResponse object.
    """

    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]
