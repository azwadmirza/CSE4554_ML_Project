    def __init__(self, file, fs=None):
        """Initialise the FSFile instance.

        *file* can be string or an fsspec.OpenFile instance. In the latter case, the follow argument *fs* has no effect.
        *fs* can be None or a fsspec filesystem instance.
        """
        try:
            self._file = file.path
            self._fs = file.fs
        except AttributeError:
            self._file = file
            self._fs = fs