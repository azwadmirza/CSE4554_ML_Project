    def from_parts(
        cls,
        scheme=None,
        host=None,
        user=None,
        port=None,
        path="",
        netloc=None,
        params=None,
        query=None,
        fragment=None,
    ):
        assert bool(host) ^ bool(netloc)

        if netloc is not None:
            return cls(
                "{}://{}{}{}{}{}".format(
                    scheme,
                    netloc,
                    path,
                    (";" + params) if params else "",
                    ("?" + query) if query else "",
                    ("#" + fragment) if fragment else "",
                )
            )

        obj = cls.__new__(cls)
        obj.fill_parts(scheme, host, user, port, path)
        obj.params = params
        obj.query = query
        obj.fragment = fragment
        return obj