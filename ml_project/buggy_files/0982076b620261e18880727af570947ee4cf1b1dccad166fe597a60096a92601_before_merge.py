    def loads(cls, string, app=None):
        # type: (unicode, Sphinx) -> BuildEnvironment
        io = StringIO(string)
        return cls.load(io, app)