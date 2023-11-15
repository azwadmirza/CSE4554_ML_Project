    def run(self, dag):
        """Expand all op nodes to the given basis.

        Args:
            dag(DAGCircuit): input dag

        Raises:
            QiskitError: if unable to unroll given the basis due to undefined
            decomposition rules (such as a bad basis) or excessive recursion.

        Returns:
            DAGCircuit: output unrolled dag
        """
        # Walk through the DAG and expand each non-basis node
        for node in dag.op_nodes():
            basic_insts = ['measure', 'reset', 'barrier', 'snapshot']
            if node.name in basic_insts:
                # TODO: this is legacy behavior.Basis_insts should be removed that these
                #  instructions should be part of the device-reported basis. Currently, no
                #  backend reports "measure", for example.
                continue
            if node.name in self.basis:  # If already a base, ignore.
                continue

            # TODO: allow choosing other possible decompositions
            try:
                rule = node.op.definition
            except TypeError as err:
                if any(isinstance(p, ParameterExpression) for p in node.op.params):
                    raise QiskitError('Unrolling gates parameterized by expressions '
                                      'is currently unsupported.')
                raise QiskitError('Error decomposing node {}: {}'.format(node.name, err))

            if not rule:
                raise QiskitError("Cannot unroll the circuit to the given basis, %s. "
                                  "No rule to expand instruction %s." %
                                  (str(self.basis), node.op.name))

            # hacky way to build a dag on the same register as the rule is defined
            # TODO: need anonymous rules to address wires by index
            decomposition = DAGCircuit()
            decomposition.add_qreg(rule[0][1][0].register)
            for inst in rule:
                decomposition.apply_operation_back(*inst)

            unrolled_dag = self.run(decomposition)  # recursively unroll ops
            dag.substitute_node_with_dag(node, unrolled_dag)
        return dag