    def __init__(self, filename="Pipfile", extra=None, **kwargs):
        extra = kwargs.pop("extra", [])
        message = ("{0} {1}".format(
                crayons.red("Aborting!", bold=True),
                crayons.white("Please ensure that the file exists and is located in your"
                              " project root directory.", bold=True)
            )
        )
        super(PipfileNotFound, self).__init__(filename, message=decode_for_output(message), extra=extra, **kwargs)