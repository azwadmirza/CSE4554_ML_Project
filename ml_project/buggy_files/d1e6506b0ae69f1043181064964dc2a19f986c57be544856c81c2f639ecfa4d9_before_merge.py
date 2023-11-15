    def issubset(self, iterable):
        other = type(self)(iterable)

        if len(self) > len(other):
            return False
        for m in itertools_filterfalse(
            other._members.__contains__, iter(self._members.keys())
        ):
            return False
        return True