    def _check_nested_function(self, node: AnyFunctionDef) -> None:
        parent = getattr(node, 'wps_parent', None)
        is_inside_function = isinstance(parent, self._function_nodes)

        if is_inside_function and node.name not in NESTED_FUNCTIONS_WHITELIST:
            self.add_violation(NestedFunctionViolation(node, text=node.name))