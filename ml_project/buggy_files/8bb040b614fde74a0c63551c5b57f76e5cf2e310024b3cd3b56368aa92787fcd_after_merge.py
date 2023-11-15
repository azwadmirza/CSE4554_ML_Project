    def _get_pointer(self):
        try:
            if self.thisdir.files[self._pointer] != self._pointed_obj:
                try:
                    self._pointer = self.thisdir.files.index(self._pointed_obj)
                except ValueError:
                    self._set_pointer(self._pointer)
        except (TypeError, IndexError):
            pass
        return self._pointer