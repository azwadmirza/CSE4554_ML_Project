    def _evaluate_qnode(self, x):
        """Evaluates the QNode for a single input datapoint.

        Args:
            x (tensor): the datapoint

        Returns:
            tensor: output datapoint
        """
        if qml.tape_mode_active():
            return self._evaluate_qnode_tape_mode(x)

        qnode = self.qnode

        for arg in self.sig:
            if arg is not self.input_arg:  # Non-input arguments must always be positional
                w = self.qnode_weights[arg].to(x)

                qnode = functools.partial(qnode, w)
            else:
                if self.input_is_default:  # The input argument can be positional or keyword
                    qnode = functools.partial(qnode, **{self.input_arg: x})
                else:
                    qnode = functools.partial(qnode, x)
        return qnode().type(x.dtype)