    def __init__(self, message=None, **kwargs):
        if not message:
            message = crayons.normal("Aborting deploy", bold=True)
        extra = kwargs.pop("extra", [])
        PipenvUsageError.__init__(self, message=fix_utf8(message), extra=extra, **kwargs)