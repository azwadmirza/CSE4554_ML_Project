    def _check_nested_classes(self, node: ast.ClassDef) -> None:
        parent = getattr(node, 'wps_parent', None)
        is_inside_class = isinstance(parent, ast.ClassDef)
        is_inside_function = isinstance(parent, self._function_nodes)

        if is_inside_class and node.name not in NESTED_CLASSES_WHITELIST:
            self.add_violation(NestedClassViolation(node, text=node.name))
        elif is_inside_function:
            self.add_violation(NestedClassViolation(node, text=node.name))