    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        input_iter = iter(inputs)
        next(input_iter)
        if isinstance(self.to_replace, SERIES_TYPE):
            self._to_replace = next(input_iter)
        if isinstance(self.value, SERIES_TYPE):
            self._value = next(input_iter)
        self._fill_chunks = list(input_iter)