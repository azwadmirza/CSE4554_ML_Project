    def _set_pointer(self, value):
        self._pointer = value
        self._pointed_obj = self.thisdir.files[self._pointer]