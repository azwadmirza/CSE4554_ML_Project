    def count_ops(self):
        """Count each operation kind in the circuit.

        Returns:
            dict: a breakdown of how many operations of each kind.
        """
        count_ops = {}
        for op in self.data:
            if op[0].name in count_ops.keys():
                count_ops[op[0].name] += 1
            else:
                count_ops[op[0].name] = 1
        return count_ops