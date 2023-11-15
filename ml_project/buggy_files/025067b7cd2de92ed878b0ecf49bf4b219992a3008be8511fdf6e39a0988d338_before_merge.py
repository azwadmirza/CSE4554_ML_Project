    def error(self, msg, *args, **kwargs):
        """Prints a formatted error message.

        For arguments, see `_format_msg`.
        """
        self._print(_format_msg(cf.red(msg), *args, **kwargs))