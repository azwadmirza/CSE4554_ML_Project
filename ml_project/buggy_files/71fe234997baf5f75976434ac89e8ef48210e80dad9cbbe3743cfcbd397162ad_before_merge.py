    def size(self):
        """Returns total number of gate operations in circuit.

        Returns:
            int: Total number of gate operations.
        """
        gate_ops = 0
        for item in self.data:
            if item.name not in ['barrier', 'snapshot']:
                gate_ops += 1
        return gate_ops