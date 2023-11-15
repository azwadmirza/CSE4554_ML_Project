    def decode(cls, encoded):
        TRACER.log("creating PythonIdentity from encoded: %s" % encoded, V=9)
        values = json.loads(encoded)
        if len(values) != 7:
            raise cls.InvalidError("Invalid interpreter identity: %s" % encoded)

        supported_tags = values.pop("supported_tags")

        def iter_tags():
            for (interpreter, abi, platform) in supported_tags:
                yield tags.Tag(interpreter=interpreter, abi=abi, platform=platform)

        return cls(supported_tags=iter_tags(), **values)