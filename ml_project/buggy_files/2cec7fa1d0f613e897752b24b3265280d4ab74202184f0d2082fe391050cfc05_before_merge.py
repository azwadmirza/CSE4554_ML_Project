    def from_parts(
        cls, scheme=None, host=None, user=None, port=None, path="", netloc=None
    ):
        assert bool(host) ^ bool(netloc)

        if netloc is not None:
            return cls("{}://{}{}".format(scheme, netloc, path))

        obj = cls.__new__(cls)
        obj.fill_parts(scheme, host, user, port, path)
        return obj