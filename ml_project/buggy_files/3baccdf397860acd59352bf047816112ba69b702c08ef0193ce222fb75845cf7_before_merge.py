    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        if not self._from_1d_tensors:
            self._input = inputs[0]
        if self._index is not None:
            self._index = inputs[-1]