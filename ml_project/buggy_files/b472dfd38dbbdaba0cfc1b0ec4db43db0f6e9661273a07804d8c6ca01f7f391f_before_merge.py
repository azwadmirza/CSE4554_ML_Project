    def warning(self, msg, *args, **kwargs):
        """Prints a formatted warning message.

        For arguments, see `_format_msg`.
        """
        self._print(_format_msg(cf.yellow(msg), *args, **kwargs))