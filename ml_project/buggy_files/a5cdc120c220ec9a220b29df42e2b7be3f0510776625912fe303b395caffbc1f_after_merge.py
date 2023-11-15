    def _evaluate_qnode_tape_mode(self, x):
        """Evaluates a tape-mode QNode for a single input datapoint.

        Args:
            x (tensor): the datapoint

        Returns:
            tensor: output datapoint
        """
        kwargs = {
            **{self.input_arg: x},
            **{arg: weight.to(x) for arg, weight in self.qnode_weights.items()},
        }
        return self.qnode(**kwargs).type(x.dtype)