    def size(self):
        self._value_buffer.seek(0, os.SEEK_END)
        return self._value_buffer.tell()