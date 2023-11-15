    def print(self, msg, *args, **kwargs):
        """Prints a message.

        For arguments, see `_format_msg`.
        """
        self._print(_format_msg(msg, *args, **kwargs))