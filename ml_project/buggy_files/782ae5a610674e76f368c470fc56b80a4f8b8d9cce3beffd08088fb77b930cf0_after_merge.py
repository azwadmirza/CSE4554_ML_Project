    def save_file(self, parsed, **kwargs):
        if self._response_key not in parsed:
            # If the response key is not in parsed, then
            # we've received an error message and we'll let the AWS CLI
            # error handler print out an error message.  We have no
            # file to save in this situation.
            return
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