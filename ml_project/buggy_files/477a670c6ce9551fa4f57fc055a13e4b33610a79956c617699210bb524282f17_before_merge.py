    def labeled_value(self, key, msg, *args, **kwargs):
        """Displays a key-value pair with special formatting.

        Args:
            key (str): Label that is prepended to the message.

        For other arguments, see `_format_msg`.
        """
        self._print(
            cf.cyan(key) + ": " + _format_msg(cf.bold(msg), *args, **kwargs))