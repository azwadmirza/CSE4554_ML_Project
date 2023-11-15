    def dir_hash(cls, d):
        # type: (str) -> str
        """Return a reproducible hash of the contents of a directory; excluding all `.pyc` files."""
        names = sorted(cls._iter_non_pyc_files(d))

        def stream_factory(name):
            # type: (str) -> IO
            return open(os.path.join(d, name), "rb")  # noqa: T802

        return cls._compute_hash(names, stream_factory)