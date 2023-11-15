    def __init__(self, message=None, **kwargs):
        if not message:
            message = crayons.normal("Aborting deploy", bold=True)
        extra = kwargs.pop("extra", [])
        PipenvUsageError.__init__(self, message=decode_for_output(message), extra=extra, **kwargs)