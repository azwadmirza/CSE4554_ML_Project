    def __init__(self, file, fs=None):
        """Initialise the FSFile instance.

        Args:
            file (str, Pathlike, or OpenFile):
                String, object implementing the `os.PathLike` protocol, or
                an `fsspec.OpenFile` instance.  If passed an instance of
                `fsspec.OpenFile`, the following argument ``fs`` has no
                effect.
            fs (fsspec filesystem, optional)
                Object implementing the fsspec filesystem protocol.
        """
        try:
            self._file = file.path
            self._fs = file.fs
        except AttributeError:
            self._file = file
            self._fs = fs