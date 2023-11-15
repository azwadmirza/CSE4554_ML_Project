    def _clear(self):
        self._reset_name()
        self._externally_defined = False
        self._is_initialized_tensor = None
        self._initial_value_tensor = None
        self._unconstrained_tensor = None
        self._constrained_tensor = None
        self._prior_tensor = None