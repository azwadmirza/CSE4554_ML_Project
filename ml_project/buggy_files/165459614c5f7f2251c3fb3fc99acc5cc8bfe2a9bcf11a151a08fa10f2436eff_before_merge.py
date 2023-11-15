    def _backtrack(self):
        """Perform backtracking.

        When we enter here, the stack is like this::

            [ state Z ]
            [ state Y ]
            [ state X ]
            .... earlier states are irrelevant.

        1. No pins worked for Z, so it does not have a pin.
        2. We want to reset state Y to unpinned, and pin another candidate.
        3. State X holds what state Y was before the pin, but does not
           have the incompatibility information gathered in state Y.

        Each iteration of the loop will:

        1.  Discard Z.
        2.  Discard Y but remember its incompatibility information gathered
            previously, and the failure we're dealing with right now.
        3.  Push a new state Y' based on X, and apply the incompatibility
            information from Y to Y'.
        4a. If this causes Y' to conflict, we need to backtrack again. Make Y'
            the new Z and go back to step 2.
        4b. If the incompatibilites apply cleanly, end backtracking.
        """
        while len(self._states) >= 3:
            # Remove the state that triggered backtracking.
            del self._states[-1]

            # Retrieve the last candidate pin and known incompatibilities.
            broken_state = self._states.pop()
            name, candidate = broken_state.mapping.popitem()
            incompatibilities_from_broken = [
                (k, v.incompatibilities)
                for k, v in broken_state.criteria.items()
            ]

            self._r.backtracking(candidate)

            # Create a new state from the last known-to-work one, and apply
            # the previously gathered incompatibility information.
            self._push_new_state()
            for k, incompatibilities in incompatibilities_from_broken:
                try:
                    crit = self.state.criteria[k]
                except KeyError:
                    continue
                self.state.criteria[k] = crit.excluded_of(incompatibilities)

            # Mark the newly known incompatibility.
            criterion = self.state.criteria[name].excluded_of([candidate])

            # It works! Let's work on this new state.
            if criterion:
                self.state.criteria[name] = criterion
                return True

            # State does not work after adding the new incompatibility
            # information. Try the still previous state.

        # No way to backtrack anymore.
        return False