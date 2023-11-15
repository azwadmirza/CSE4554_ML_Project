    def handle_exception(self, exc_val, exc_tb):
        return_code = getattr(exc_val, 'return_code', None)
        if return_code == 0:
            return 0
        if isinstance(exc_val, CondaError):
            return self.handle_application_exception(exc_val, exc_tb)
        if isinstance(exc_val, UnicodeError) and PY2:
            return self.handle_application_exception(EncodingError(exc_val), exc_tb)
        if isinstance(exc_val, EnvironmentError):
            if getattr(exc_val, 'errno', None) == ENOSPC:
                return self.handle_application_exception(NoSpaceLeftError(exc_val), exc_tb)
        if isinstance(exc_val, KeyboardInterrupt):
            self._print_conda_exception(CondaError("KeyboardInterrupt"), _format_exc())
            return 1
        if isinstance(exc_val, SystemExit):
            return exc_val.code
        return self.handle_unexpected_exception(exc_val, exc_tb)