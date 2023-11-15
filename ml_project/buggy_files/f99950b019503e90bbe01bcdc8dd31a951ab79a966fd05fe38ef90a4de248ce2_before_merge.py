    def run(self, dag):
        """Expand 3+ qubit gates using their decomposition rules.

        Args:
            dag(DAGCircuit): input dag
        Returns:
            DAGCircuit: output dag with maximum node degrees of 2
        Raises:
            QiskitError: if a 3q+ gate is not decomposable
        """
        for node in dag.threeQ_or_more_gates():
            # TODO: allow choosing other possible decompositions
            rule = node.op.definition
            if not rule:
                raise QiskitError("Cannot unroll all 3q or more gates. "
                                  "No rule to expand instruction %s." %
                                  node.op.name)

            # hacky way to build a dag on the same register as the rule is defined
            # TODO: need anonymous rules to address wires by index
            decomposition = DAGCircuit()
            decomposition.add_qreg(rule[0][1][0].register)
            for inst in rule:
                decomposition.apply_operation_back(*inst)
            decomposition = self.run(decomposition)  # recursively unroll
            dag.substitute_node_with_dag(node, decomposition)
        return dag