    def visit_ClassDef(self, node):  # type: (ast.ClassDef) -> None
        for decorator in node.decorator_list:
            if self._is_six(decorator, ('python_2_unicode_compatible',)):
                self.six_remove_decorators.add(_ast_to_offset(decorator))

        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'object':
                self.bases_to_remove.add(_ast_to_offset(base))
            elif self._is_six(base, ('Iterator',)):
                self.bases_to_remove.add(_ast_to_offset(base))

        if (
                len(node.bases) == 1 and
                isinstance(node.bases[0], ast.Call) and
                self._is_six(node.bases[0].func, ('with_metaclass',))
        ):
            self.six_with_metaclass.add(_ast_to_offset(node.bases[0]))

        self._class_info_stack.append(FindPy3Plus.ClassInfo(node.name))
        self.generic_visit(node)
        self._class_info_stack.pop()