    def write_error(self, status_code, *args, **kwargs):
        """Only send traceback if app.DEVELOPER is true."""
        response = None
        exc_info = kwargs.get('exc_info', None)

        if exc_info and isinstance(exc_info[1], HTTPError):
            error = exc_info[1].log_message or exc_info[1].reason
            response = self.api_response(status=status_code, error=error)
        elif app.DEVELOPER and exc_info:
            self.set_header('content-type', 'text/plain')
            self.set_status(500)
            for line in traceback.format_exception(*exc_info):
                self.write(line)
        else:
            response = self._internal_server_error()

        self.finish(response)