    def __eq__(self, other):
        if type(self) is not type(other):
            return False

        var1 = self._get_identical_source(self)
        var2 = self._get_identical_source(other)
        # pylint: disable=protected-access
        return var1.name == var2.name \
               and var1._compute_value == var2._compute_value