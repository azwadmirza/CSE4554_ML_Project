    def raise_if_problem(self, exceptionType=Error):
        try:
            _exception_from_error_queue(exceptionType)
        except exceptionType as e:
            from_queue = e
        if self._problems:
            raise self._problems[0]
        return from_queue