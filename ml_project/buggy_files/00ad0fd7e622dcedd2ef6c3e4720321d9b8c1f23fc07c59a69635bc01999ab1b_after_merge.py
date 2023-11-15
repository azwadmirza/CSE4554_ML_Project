    def apply(self, other):
        if type(other) == date:
            other = datetime(other.year, other.month, other.day)

        if isinstance(other, (datetime, timedelta)):
            return other + self.delta
        elif isinstance(other, type(self)):
            return type(self)(self.n + other.n)
        else:  # pragma: no cover
            raise TypeError('Unhandled type: %s' % type(other))