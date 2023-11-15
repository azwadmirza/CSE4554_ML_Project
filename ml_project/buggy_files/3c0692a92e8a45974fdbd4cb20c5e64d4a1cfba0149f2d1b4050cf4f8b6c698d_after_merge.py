    def _raise_304_if_not_modified(self, record=None):
        """Raise 304 if current timestamp is inferior to the one specified
        in headers.

        :raises: :exc:`~pyramid:pyramid.httpexceptions.HTTPNotModified`
        """
        if_none_match = self.request.headers.get('If-None-Match')

        if not if_none_match:
            return

        error_details = {
            'location': 'header',
            'description': "Invalid value for If-None-Match"
        }

        try:
            if_none_match = decode_header(if_none_match)
        except UnicodeDecodeError:
            raise_invalid(self.request, **error_details)

        try:
            if not (if_none_match[0] == if_none_match[-1] == '"'):
                raise ValueError()
            modified_since = int(if_none_match[1:-1])
        except (IndexError, ValueError):
            if if_none_match == '*':
                return
            raise_invalid(self.request, **error_details)

        if record:
            current_timestamp = record[self.model.modified_field]
        else:
            current_timestamp = self.model.timestamp()

        if current_timestamp <= modified_since:
            response = HTTPNotModified()
            self._add_timestamp_header(response, timestamp=current_timestamp)
            raise response