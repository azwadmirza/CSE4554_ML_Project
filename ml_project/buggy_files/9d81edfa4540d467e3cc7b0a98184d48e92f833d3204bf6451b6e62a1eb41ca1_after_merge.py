    def _raise_passphrase_exception(self):
        if self._passphrase_helper is not None:
            self._passphrase_helper.raise_if_problem(Error)

        _raise_current_error()