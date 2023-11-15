    def new_tensors(self, inputs, shape, **kw):
        indexes = kw.pop('indexes', None)
        with self._handle_params(inputs, indexes) as mix_inputs:
            return super(TensorIndex, self).new_tensors(mix_inputs, shape, **kw)