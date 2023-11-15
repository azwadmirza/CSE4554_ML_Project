    def error(self, msg, *args, **kwargs):
        """Prints a formatted error message.

        For arguments, see `_format_msg`.
        """
        self.print(cf.red(msg), *args, **kwargs)