    def symmetric_difference(self, iterable):
        result = self.__class__()
        members = self._members
        other = {id(obj): obj for obj in iterable}
        result._members.update(
            ((k, v) for k, v in members.items() if k not in other)
        )
        result._members.update(
            ((k, v) for k, v in other.items() if k not in members)
        )
        return result