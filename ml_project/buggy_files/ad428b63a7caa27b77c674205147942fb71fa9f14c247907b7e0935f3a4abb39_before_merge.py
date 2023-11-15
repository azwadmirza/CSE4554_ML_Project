    def __str__(self):
        items = 'name value path domain secure httpOnly expiry'.split()
        return '\n'.join('%s=%s' % (item, getattr(self, item))
                         for item in items)