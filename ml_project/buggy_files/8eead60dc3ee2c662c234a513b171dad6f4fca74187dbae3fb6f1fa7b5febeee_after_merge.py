    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        inputs_iter = iter(self._inputs)
        self._input = next(inputs_iter)
        if isinstance(self._bins, (TENSOR_TYPE, TENSOR_CHUNK_TYPE)):
            self._bins = next(inputs_iter)
        if self._weights is not None:
            self._weights = next(inputs_iter)
        if self._input_min is not None:
            self._input_min = next(inputs_iter)
        if self._input_max is not None:
            self._input_max = next(inputs_iter)