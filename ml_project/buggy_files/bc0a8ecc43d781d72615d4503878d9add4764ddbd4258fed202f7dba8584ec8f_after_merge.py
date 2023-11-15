    def difference(self, iterable):
        result = self.__class__()
        members = self._members
        other = {id(obj) for obj in iterable}
        result._members.update(
            ((k, v) for k, v in members.items() if k not in other)
        )
        return result