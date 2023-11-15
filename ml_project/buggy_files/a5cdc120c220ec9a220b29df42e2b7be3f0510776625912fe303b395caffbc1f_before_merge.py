    def _evaluate_qnode_tape_mode(self, x):
        """Evaluates a tape-mode QNode for a single input datapoint.

        Args:
            x (tensor): the datapoint

        Returns:
            tensor: output datapoint
        """
        kwargs = {**{self.input_arg: x}, **self.qnode_weights}
        return self.qnode(**kwargs).type(x.dtype)