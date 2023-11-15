    def loads(cls, string, app=None):
        # type: (unicode, Sphinx) -> BuildEnvironment
        io = BytesIO(string)
        return cls.load(io, app)