    def dumps(cls, env):
        # type: (BuildEnvironment) -> unicode
        io = StringIO()
        cls.dump(env, io)
        return io.getvalue()