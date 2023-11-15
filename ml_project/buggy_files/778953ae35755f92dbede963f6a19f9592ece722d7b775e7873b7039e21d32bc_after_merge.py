    def _set_pointer(self, value):
        self._pointer = value
        try:
            self._pointed_obj = self.thisdir.files[self._pointer]
        except (TypeError, IndexError):
            pass