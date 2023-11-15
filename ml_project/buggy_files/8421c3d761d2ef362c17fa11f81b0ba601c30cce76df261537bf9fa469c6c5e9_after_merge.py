    def issuperset(self, iterable):
        other = self.__class__(iterable)

        if len(self) < len(other):
            return False

        for m in itertools_filterfalse(
            self._members.__contains__, iter(other._members.keys())
        ):
            return False
        return True