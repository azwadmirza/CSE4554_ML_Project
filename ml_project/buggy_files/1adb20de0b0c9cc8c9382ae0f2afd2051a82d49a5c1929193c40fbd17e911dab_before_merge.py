    def __call__(self, input_tensor, index, columns):
        if self._from_1d_tensors:
            return self._call_input_1d_tensors(input_tensor, index, columns)
        else:
            return self._call_input_tensor(input_tensor, index, columns)