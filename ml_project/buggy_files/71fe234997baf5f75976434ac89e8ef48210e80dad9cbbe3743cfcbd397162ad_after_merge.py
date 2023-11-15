    def size(self):
        """Returns total number of gate operations in circuit.

        Returns:
            int: Total number of gate operations.
        """
        gate_ops = 0
        for instr, _, _ in self.data:
            if instr.name not in ['barrier', 'snapshot']:
                gate_ops += 1
        return gate_ops