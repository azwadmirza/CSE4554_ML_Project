    def pex_hash(cls, d):
        # type: (str) -> str
        """Return a reproducible hash of the contents of a directory."""
        names = sorted(
            f for f in cls._iter_files(d) if not (f.endswith(".pyc") or f.startswith("."))
        )

        def stream_factory(name):
            # type: (str) -> IO
            return open(os.path.join(d, name), "rb")  # noqa: T802

        return cls._compute_hash(names, stream_factory)