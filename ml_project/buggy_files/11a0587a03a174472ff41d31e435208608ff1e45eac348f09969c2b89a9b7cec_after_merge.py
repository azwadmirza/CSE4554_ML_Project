    def success(self, msg, *args, **kwargs):
        """Prints a formatted success message.

        For arguments, see `_format_msg`.
        """
        self.print(cf.green(msg), *args, **kwargs)