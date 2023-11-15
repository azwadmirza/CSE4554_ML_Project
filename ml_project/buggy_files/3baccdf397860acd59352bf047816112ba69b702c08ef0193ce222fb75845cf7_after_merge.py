    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        inputs_iter = iter(self._inputs)
        if self._input is not None:
            if not isinstance(self._input, dict):
                self._input = next(inputs_iter)
            else:
                # check each value for input
                new_input = OrderedDict()
                for k, v in self._input.items():
                    if isinstance(v, (Base, Entity)):
                        new_input[k] = next(inputs_iter)
                    else:
                        new_input[k] = v
                self._input = new_input

        if self._index is not None:
            self._index = next(inputs_iter)