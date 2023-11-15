    def read(self, filenames, encoding=None):
        super().read(filenames=filenames, encoding=encoding)
        self._validate()