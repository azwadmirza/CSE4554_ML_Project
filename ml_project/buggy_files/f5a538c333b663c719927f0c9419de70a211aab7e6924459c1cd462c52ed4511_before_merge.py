    def __init__(self, path, **kwargs):
        message = "{0} {1} {2}\n{0}".format(
            crayons.red("ERROR:", bold=True),
            crayons.blue("Corrupt cache file"),
            crayons.white(path),
            crayons.white('Consider trying "pipenv lock --clear" to clear the cache.')
        )
        super(PipenvException, self).__init__(message=fix_utf8(message))