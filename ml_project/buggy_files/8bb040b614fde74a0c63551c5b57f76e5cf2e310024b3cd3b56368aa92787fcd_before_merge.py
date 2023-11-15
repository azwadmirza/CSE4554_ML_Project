    def _get_pointer(self):
        if (
                self.thisdir is not None
                and self.thisdir.files[self._pointer] != self._pointed_obj
        ):
            try:
                self._pointer = self.thisdir.files.index(self._pointed_obj)
            except ValueError:
                self._pointed_obj = self.thisdir.files[self._pointer]
        return self._pointer