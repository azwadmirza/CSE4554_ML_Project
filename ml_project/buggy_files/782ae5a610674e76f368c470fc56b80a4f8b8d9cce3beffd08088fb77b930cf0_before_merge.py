    def save_file(self, parsed, **kwargs):
        body = parsed[self._response_key]
        buffer_size = self._buffer_size
        with open(self._output_file, 'wb') as fp:
            data = body.read(buffer_size)
            while data:
                fp.write(data)
                data = body.read(buffer_size)
        # We don't want to include the streaming param in
        # the returned response.
        del parsed[self._response_key]