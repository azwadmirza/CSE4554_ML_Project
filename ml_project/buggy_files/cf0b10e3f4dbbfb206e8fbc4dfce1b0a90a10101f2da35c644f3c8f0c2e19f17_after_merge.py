    def raise_if_problem(self, exceptionType=Error):
        if self._problems:

            # Flush the OpenSSL error queue
            try:
                _exception_from_error_queue(exceptionType)
            except exceptionType:
                pass

            raise self._problems.pop(0)