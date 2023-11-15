    def warning(self, msg, *args, **kwargs):
        """Prints a formatted warning message.

        For arguments, see `_format_msg`.
        """
        self.print(cf.yellow(msg), *args, **kwargs)