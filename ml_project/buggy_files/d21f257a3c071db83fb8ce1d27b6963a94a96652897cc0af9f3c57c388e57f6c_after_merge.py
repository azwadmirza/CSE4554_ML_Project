    def __call__(self, input_tensor, index, columns):
        if isinstance(input_tensor, dict):
            return self._call_input_1d_tileables(input_tensor, index, columns)
        elif input_tensor is not None:
            return self._call_input_tensor(input_tensor, index, columns)
        else:
            return self._call_tensor_none(index, columns)