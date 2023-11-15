    def read(self, size=-1):
        """Read up to size bytes from the object and return them."""
        if size <= 0:
            if len(self._buffer):
                from_buf = self._read_from_buffer(len(self._buffer))
            else:
                from_buf = b''
            self._current_pos = self._content_length
            return from_buf + self._raw_reader.read()

        #
        # Return unused data first
        #
        if len(self._buffer) >= size:
            return self._read_from_buffer(size)

        #
        # If the stream is finished, return what we have.
        #
        if self._eof:
            return self._read_from_buffer(len(self._buffer))

        #
        # Fill our buffer to the required size.
        #
        # logger.debug('filling %r byte-long buffer up to %r bytes', len(self._buffer), size)
        self._fill_buffer(size)
        return self._read_from_buffer(size)