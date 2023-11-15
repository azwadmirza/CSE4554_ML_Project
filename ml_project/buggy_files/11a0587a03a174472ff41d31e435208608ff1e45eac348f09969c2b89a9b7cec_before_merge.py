    def success(self, msg, *args, **kwargs):
        """Prints a formatted success message.

        For arguments, see `_format_msg`.
        """
        self._print(_format_msg(cf.green(msg), *args, **kwargs))