    def intersection(self, iterable):
        result = self.__class__()
        members = self._members
        other = {id(obj) for obj in iterable}
        result._members.update(
            (k, v) for k, v in members.items() if k in other
        )
        return result