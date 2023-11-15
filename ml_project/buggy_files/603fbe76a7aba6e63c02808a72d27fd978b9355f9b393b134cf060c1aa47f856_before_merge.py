    def _clear(self):
        self._reset_name()
        self._externally_defined = False   # pylint: disable=W0201
        self._initial_value_tensor = None  # pylint: disable=W0201
        self._unconstrained_tensor = None  # pylint: disable=W0201
        self._constrained_tensor = None    # pylint: disable=W0201
        self._prior_tensor = None          # pylint: disable=W0201