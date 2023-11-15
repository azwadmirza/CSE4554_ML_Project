    def _raise_passphrase_exception(self):
        if self._passphrase_helper is None:
            _raise_current_error()
        exception = self._passphrase_helper.raise_if_problem(Error)
        if exception is not None:
            raise exception