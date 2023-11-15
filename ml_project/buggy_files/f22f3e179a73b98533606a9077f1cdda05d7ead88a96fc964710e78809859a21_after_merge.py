    def __eq__(self, other):
        if isinstance(other, basestring):
            other = Quality(other)
        if not isinstance(other, Quality):
            if other is None:
                return False
            raise TypeError('Cannot compare %r and %r' % (self, other))
        return self._comparator == other._comparator