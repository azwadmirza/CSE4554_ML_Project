    def __lt__(self, other):
        if isinstance(other, basestring):
            other = Quality(other)
            if not other:
                raise TypeError('`%s` does not appear to be a valid quality string.' % other.text)
        if not isinstance(other, Quality):
            raise TypeError('Cannot compare %r and %r' % (self, other))
        return self._comparator < other._comparator