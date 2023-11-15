    def _raise_412_if_modified(self, record=None):
        """Raise 412 if current timestamp is superior to the one
        specified in headers.

        :raises:
            :exc:`~pyramid:pyramid.httpexceptions.HTTPPreconditionFailed`
        """
        if_match = self.request.headers.get('If-Match')
        if_none_match = self.request.headers.get('If-None-Match')

        if not if_match and not if_none_match:
            return

        if_match = decode_header(if_match) if if_match else None

        if record and if_none_match and decode_header(if_none_match) == '*':
            if record.get(self.model.deleted_field, False):
                # Tombstones should not prevent creation.
                return
            modified_since = -1  # Always raise.
        elif if_match:
            try:
                if not (if_match[0] == if_match[-1] == '"'):
                    raise ValueError()
                modified_since = int(if_match[1:-1])
            except (IndexError, ValueError):
                message = ("Invalid value for If-Match. The value should "
                           "be integer between double quotes.")
                error_details = {
                    'location': 'header',
                    'description': message
                }
                raise_invalid(self.request, **error_details)
        else:
            # In case _raise_304_if_not_modified() did not raise.
            return

        if record:
            current_timestamp = record[self.model.modified_field]
        else:
            current_timestamp = self.model.timestamp()

        if current_timestamp > modified_since:
            error_msg = 'Resource was modified meanwhile'
            details = {'existing': record} if record else {}
            response = http_error(HTTPPreconditionFailed(),
                                  errno=ERRORS.MODIFIED_MEANWHILE,
                                  message=error_msg,
                                  details=details)
            self._add_timestamp_header(response, timestamp=current_timestamp)
            raise response