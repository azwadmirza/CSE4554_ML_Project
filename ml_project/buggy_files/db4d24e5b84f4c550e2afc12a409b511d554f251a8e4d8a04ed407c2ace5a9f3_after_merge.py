    def dumps(cls, env):
        # type: (BuildEnvironment) -> unicode
        io = BytesIO()
        cls.dump(env, io)
        return io.getvalue()