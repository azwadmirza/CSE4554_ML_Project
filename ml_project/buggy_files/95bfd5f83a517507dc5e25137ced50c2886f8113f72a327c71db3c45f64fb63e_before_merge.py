    def _check_redefinition(self, redeftype, node):
        """check for redefinition of a function / method / class name"""
        defined_self = node.parent.frame()[node.name]
        if defined_self is not node and not astroid.are_exclusive(node, defined_self):
            dummy_variables_rgx = lint_utils.get_global_option(
                self, 'dummy-variables-rgx', default=None)
            if dummy_variables_rgx and dummy_variables_rgx.match(defined_self.name):
                return
            self.add_message('function-redefined', node=node,
                             args=(redeftype, defined_self.fromlineno))