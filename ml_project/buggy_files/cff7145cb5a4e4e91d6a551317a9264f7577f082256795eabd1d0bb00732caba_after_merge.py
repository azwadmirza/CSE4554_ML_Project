    def check_attribute_name(self, node: ast.ClassDef) -> None:
        top_level_assigns = [
            sub_node
            for sub_node in node.body
            if isinstance(sub_node, ast.Assign)
        ]

        for assignment in top_level_assigns:
            for target in assignment.targets:
                if not isinstance(target, ast.Name):
                    continue

                name: Optional[str] = getattr(target, 'id', None)
                if name and logical.is_upper_case_name(name):
                    self._error_callback(
                        naming.UpperCaseAttributeViolation(target, text=name),
                    )