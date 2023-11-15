    def append_to_value(self, value):
        self.contentsize += len(value)
        self._value_buffer.seek(0, os.SEEK_END)
        self._value_buffer.write(value)

        self.last_modified = datetime.datetime.utcnow()
        self._etag = None  # must recalculate etag
        if self._is_versioned:
            self._version_id = str(uuid.uuid4())
        else:
            self._version_id = None