    def constraints(self):
        return set(
            self._group_constraints(
                chain(
                    sorted(self.our_constraints, key=str),
                    sorted(self.their_constraints, key=str),
                )
            )
        )