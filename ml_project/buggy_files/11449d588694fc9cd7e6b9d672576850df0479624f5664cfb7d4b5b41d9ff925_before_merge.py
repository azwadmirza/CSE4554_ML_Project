    def _copy(self, **overwrite_params):
        """
        Helper function to copy the node, replacing some values.
        """
        params = {
            "func": self._func,
            "inputs": self._inputs,
            "outputs": self._outputs,
            "name": self._name,
            "tags": self._tags,
            "decorators": self._decorators,
        }
        params.update(overwrite_params)
        return Node(**params)