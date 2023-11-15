    def group(self, msg, *args, **kwargs):
        """Print a group title in a special color and start an indented block.

        For arguments, see `_format_msg`.
        """
        self.print(cf.cornflowerBlue(msg), *args, **kwargs)

        return self.indented()