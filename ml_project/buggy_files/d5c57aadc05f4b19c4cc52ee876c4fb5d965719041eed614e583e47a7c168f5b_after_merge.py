    def run(self, dag):
        """Expand a given gate into its decomposition.

        Args:
            dag(DAGCircuit): input dag
        Returns:
            DAGCircuit: output dag where gate was expanded.
        """
        # Walk through the DAG and expand each non-basis node
        for node in dag.op_nodes(self.gate):
            # opaque or built-in gates are not decomposable
            if not node.op.definition:
                continue
            # TODO: allow choosing among multiple decomposition rules
            rule = node.op.definition
            # hacky way to build a dag on the same register as the rule is defined
            # TODO: need anonymous rules to address wires by index
            decomposition = DAGCircuit()
            qregs = {qb.register for inst in rule for qb in inst[1]}
            cregs = {cb.register for inst in rule for cb in inst[2]}
            for qreg in qregs:
                decomposition.add_qreg(qreg)
            for creg in cregs:
                decomposition.add_creg(creg)
            for inst in rule:
                decomposition.apply_operation_back(*inst)
            dag.substitute_node_with_dag(node, decomposition)
        return dag