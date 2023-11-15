    def __init__(self, path, **kwargs):
        message = "{0} {1} {2}\n{0}".format(
            crayons.red("ERROR:", bold=True),
            crayons.blue("Corrupt cache file"),
            crayons.white(path),
            crayons.white('Consider trying "pipenv lock --clear" to clear the cache.')
        )
        PipenvException.__init__(self, message=decode_for_output(message))