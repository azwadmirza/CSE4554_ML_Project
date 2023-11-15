    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        self._input = self._inputs[0]
        if isinstance(self._tree, (OBJECT_TYPE, OBJECT_CHUNK_TYPE)):
            self._tree = self._inputs[1]