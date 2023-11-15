    def __str__(self):
        items = 'name value path domain secure httpOnly expiry'.split()
        string = '\n'.join('%s=%s' % (item, getattr(self, item))
                           for item in items)
        if self.extra:
            string = '%s\n%s=%s\n' % (string, 'extra', self.extra)
        return string