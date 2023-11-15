    def __str__(self):
        """Stringify the exception."""
        return 'cannot find language {0}'.format(self.lang)