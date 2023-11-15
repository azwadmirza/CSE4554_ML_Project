    def _parse_variable_definition_init_tuple(self, statement, index, node):
        local_var = LocalVariableInitFromTupleSolc(statement, index)
        #local_var = LocalVariableSolc(statement[self.get_children('children')][0], statement[self.get_children('children')][1::])
        local_var.set_function(self)
        local_var.set_offset(statement['src'], self.contract.slither)

        self._add_local_variable(local_var)
#        local_var.analyze(self)

        new_node = self._new_node(NodeType.VARIABLE, statement['src'])
        new_node.add_variable_declaration(local_var)
        link_nodes(node, new_node)
        return new_node