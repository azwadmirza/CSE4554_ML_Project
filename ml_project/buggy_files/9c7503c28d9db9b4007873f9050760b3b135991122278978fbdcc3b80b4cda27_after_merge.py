    def __setstate__(self, state):
        """
        Necessary for making this object picklable.
        """

        if isinstance(state, dict):
            self._data = state.pop("data")
            for k, v in state.items():
                setattr(self, k, v)

        elif isinstance(state, tuple):

            if len(state) == 2:
                nd_state, own_state = state
                data = np.empty(nd_state[1], dtype=nd_state[2])
                np.ndarray.__setstate__(data, nd_state)
                self._name = own_state[0]

            else:  # pragma: no cover
                data = np.empty(state)
                np.ndarray.__setstate__(data, state)

            self._data = data
            self._reset_identity()
        else:
            raise Exception("invalid pickle state")