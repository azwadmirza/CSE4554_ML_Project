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
            decomposition.add_qreg(rule[0][1][0].register)
            if rule[0][2]:
                decomposition.add_creg(rule[0][2][0].register)
            for inst in rule:
                decomposition.apply_operation_back(*inst)
            dag.substitute_node_with_dag(node, decomposition)
        return dag