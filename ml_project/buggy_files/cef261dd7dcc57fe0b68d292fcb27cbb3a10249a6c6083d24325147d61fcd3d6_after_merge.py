    def __str__(self):
        """String representation.

        :return:
        :rtype: str
        """
        result = str(self.fmt)
        return result.format(*self.args, **self.kwargs) if self.args or self.kwargs else result