    def new_tensors(self, inputs, shape, **kw):
        tensor, indexes, value = inputs
        self._indexes = indexes
        self._value = value
        inputs = self._handle_inputs(inputs)
        return super(TensorIndexSetValue, self).new_tensors(inputs, shape, **kw)