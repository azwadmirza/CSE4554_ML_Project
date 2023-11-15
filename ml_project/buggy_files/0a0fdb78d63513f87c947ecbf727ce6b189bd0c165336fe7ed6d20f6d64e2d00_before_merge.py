    def __init__(self, filename, message=None, **kwargs):
        extra = kwargs.pop("extra", [])
        if not message:
            message = crayons.white("Please ensure that the file exists!", bold=True)
        message = self.formatted_message.format(
            crayons.white("{0} not found!".format(filename), bold=True),
            message
        )
        FileError.__init__(self, filename=filename, hint=fix_utf8(message), **kwargs)
        self.extra = extra