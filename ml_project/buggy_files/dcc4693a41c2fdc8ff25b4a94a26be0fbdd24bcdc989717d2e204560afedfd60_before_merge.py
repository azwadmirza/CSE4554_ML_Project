    def new_tensors(self, inputs, shape, **kw):
        tensor, indexes = inputs
        self._indexes = indexes
        inputs = self._handle_inputs(inputs)
        return super(TensorIndex, self).new_tensors(inputs, shape, **kw)