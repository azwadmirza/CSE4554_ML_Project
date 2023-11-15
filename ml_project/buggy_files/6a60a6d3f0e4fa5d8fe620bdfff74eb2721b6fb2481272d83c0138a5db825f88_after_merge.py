    def _parse_dowhile(self, doWhilestatement, node):

        node_startDoWhile = self._new_node(NodeType.STARTLOOP, doWhilestatement['src'])
        node_condition = self._new_node(NodeType.IFLOOP, doWhilestatement['src'])

        if self.is_compact_ast:
            node_condition.add_unparsed_expression(doWhilestatement['condition'])
            statement = self._parse_statement(doWhilestatement['body'], node_condition)
        else:
            children = doWhilestatement[self.get_children('children')]
            # same order in the AST as while
            expression = children[0]
            node_condition.add_unparsed_expression(expression)
            statement = self._parse_statement(children[1], node_condition)

        node_endDoWhile = self._new_node(NodeType.ENDLOOP, doWhilestatement['src'])

        link_nodes(node, node_startDoWhile)
        # empty block, loop from the start to the condition
        if not node_condition.sons:
            link_nodes(node_startDoWhile, node_condition)
        else:
            link_nodes(node_startDoWhile, node_condition.sons[0])
        link_nodes(statement, node_condition)
        link_nodes(node_condition, node_endDoWhile)
        return node_endDoWhile