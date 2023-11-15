    def new_chunks(self, inputs, shape, **kw):
        indexes = kw.pop('indexes', None)
        value = kw.pop('value', None)
        with self._handle_params(inputs, indexes, value) as mix_inputs:
            return super(TensorIndexSetValue, self).new_chunks(mix_inputs, shape, **kw)