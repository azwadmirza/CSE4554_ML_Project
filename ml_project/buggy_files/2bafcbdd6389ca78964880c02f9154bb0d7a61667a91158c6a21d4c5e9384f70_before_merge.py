    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        self._input = self._inputs[0]
        if isinstance(self._q, TENSOR_TYPE):
            self._q = self._inputs[-1]