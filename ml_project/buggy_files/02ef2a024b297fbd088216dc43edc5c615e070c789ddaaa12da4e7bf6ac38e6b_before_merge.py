    def read(self, size=-1):
        if self.position == self._content_length:
            return b''
        if size <= 0:
            end = None
        else:
            end = min(self._content_length, self.position + size)
        range_string = _range_string(self.position, stop=end)
        logger.debug('range_string: %r', range_string)
        body = self._object.get(Range=range_string)['Body'].read()
        self.position += len(body)
        return body