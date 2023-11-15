    def __str__(self):
        """String representation.

        :return:
        :rtype: str
        """
        return str(self.fmt).format(*self.args, **self.kwargs)