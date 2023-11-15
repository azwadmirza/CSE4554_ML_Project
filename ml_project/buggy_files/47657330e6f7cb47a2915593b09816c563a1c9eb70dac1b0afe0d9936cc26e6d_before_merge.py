    def visit_Bytes(self, node):
        '''Visitor for AST Bytes nodes

        add relevant information about node to
        the context for use in tests which inspect strings.
        :param node: The node that is being inspected
        :return: -
        '''
        self.context['bytes'] = node.s
        if not isinstance(node.parent, ast.Expr):  # docstring
            self.context['linerange'] = b_utils.linerange_fix(node.parent)
            self.update_scores(self.tester.run_tests(self.context, 'Bytes'))