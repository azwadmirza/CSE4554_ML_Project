    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        self._input = self._inputs[0]
        if self._index is not None:
            self._index = self._inputs[-1]