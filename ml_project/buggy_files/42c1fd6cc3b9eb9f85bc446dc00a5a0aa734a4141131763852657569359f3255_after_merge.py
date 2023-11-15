    def write_error(self, status_code, **kwargs):
        """Write JSON errors instead of HTML"""
        exc_info = kwargs.get('exc_info')
        message = ''
        exception = None
        status_message = responses.get(status_code, 'Unknown Error')
        if exc_info:
            exception = exc_info[1]
            # get the custom message, if defined
            try:
                message = exception.log_message % exception.args
            except Exception:
                pass

            # construct the custom reason, if defined
            reason = getattr(exception, 'reason', '')
            if reason:
                status_message = reason

        if exception and isinstance(exception, SQLAlchemyError):
            self.log.warning("Rolling back session due to database error %s", exception)
            self.db.rollback()

        self.set_header('Content-Type', 'application/json')
        # allow setting headers from exceptions
        # since exception handler clears headers
        headers = getattr(exception, 'headers', None)
        if headers:
            for key, value in headers.items():
                self.set_header(key, value)

        self.write(json.dumps({
            'status': status_code,
            'message': message or status_message,
        }))