    def apply_gradients(self, grads_and_vars, name=None, **kwargs):
        self._optimizer._iterations = (
            self.iterations
        )  # pylint: disable=protected-access
        return super().apply_gradients(grads_and_vars, name, **kwargs)