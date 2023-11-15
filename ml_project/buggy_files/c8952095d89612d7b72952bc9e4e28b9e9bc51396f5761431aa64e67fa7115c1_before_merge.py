    def __init__(self, option_name, message=None, ctx=None, **kwargs):
        extra = kwargs.pop("extra", [])
        PipenvUsageError.__init__(self, message=fix_utf8(message), ctx=ctx, **kwargs)
        self.extra = extra
        self.option_name = option_name