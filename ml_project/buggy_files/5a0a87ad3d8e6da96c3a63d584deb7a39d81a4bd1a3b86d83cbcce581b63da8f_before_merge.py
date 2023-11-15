    def new_chunks(self, inputs, shape, **kw):
        chunk, indexes = inputs
        self._indexes = indexes
        inputs = self._handle_inputs(inputs)
        return super(TensorIndex, self).new_chunks(inputs, shape, **kw)