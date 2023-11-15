    def pex_hash(cls, d):
        # type: (str) -> str
        """Return a reproducible hash of the contents of a loose PEX; excluding all `.pyc` files."""
        names = sorted(f for f in cls._iter_non_pyc_files(d) if not f.startswith("."))

        def stream_factory(name):
            # type: (str) -> IO
            return open(os.path.join(d, name), "rb")  # noqa: T802

        return cls._compute_hash(names, stream_factory)