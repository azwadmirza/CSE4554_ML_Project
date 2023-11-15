    def symmetric_difference(self, iterable):
        result = type(self)()
        # testlib.pragma exempt:__hash__
        members = self._member_id_tuples()
        other = _iter_id(iterable)
        result._members.update(
            self._working_set(members).symmetric_difference(other)
        )
        return result