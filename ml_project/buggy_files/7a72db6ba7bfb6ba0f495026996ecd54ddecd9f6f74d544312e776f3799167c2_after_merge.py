    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        if len(self._inputs) == 2:
            self._lhs = self._inputs[0]
            self._rhs = self._inputs[1]
        else:
            if isinstance(self._lhs, (Base, Entity)):
                self._lhs = self._inputs[0]
            elif pd.api.types.is_scalar(self._lhs):
                self._rhs = self._inputs[0]