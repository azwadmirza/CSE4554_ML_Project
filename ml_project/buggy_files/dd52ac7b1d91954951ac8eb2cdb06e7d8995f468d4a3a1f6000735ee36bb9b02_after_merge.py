    def __init__(self, output):
        super(OutputNotFoundError, self).__init__(
            "unable to find stage file with output '{path}'".format(
                path=relpath(output)
            )
        )