    def new_chunks(self, inputs, shape, **kw):
        chunk, indexes, value = inputs
        self._indexes = indexes
        self._value = value
        inputs = self._handle_inputs(inputs)
        return super(TensorIndexSetValue, self).new_chunks(inputs, shape, **kw)