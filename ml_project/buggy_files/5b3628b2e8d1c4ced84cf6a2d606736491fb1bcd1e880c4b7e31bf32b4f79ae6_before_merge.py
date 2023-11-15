    def constraints(self):
        return set(
            self._group_constraints(chain(self.our_constraints, self.their_constraints))
        )