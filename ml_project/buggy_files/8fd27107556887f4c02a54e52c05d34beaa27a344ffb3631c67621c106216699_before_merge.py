    def visit_Call(self, node):  # type: (ast.Call) -> None
        if (
                isinstance(node.func, ast.Name) and
                node.func.id in {'isinstance', 'issubclass'} and
                len(node.args) == 2 and
                self._is_six(node.args[1], SIX_TYPE_CTX_ATTRS)
        ):
            self.six_type_ctx[_ast_to_offset(node.args[1])] = node.args[1]
        elif self._is_six(node.func, ('b',)):
            self.six_b.add(_ast_to_offset(node))
        elif self._is_six(node.func, SIX_CALLS):
            self.six_calls[_ast_to_offset(node)] = node
        elif (
                isinstance(self._previous_node, ast.Expr) and
                self._is_six(node.func, SIX_RAISES)
        ):
            self.six_raises[_ast_to_offset(node)] = node
        elif (
                not self._in_comp and
                self._class_info_stack and
                self._class_info_stack[-1].def_depth == 1 and
                isinstance(node.func, ast.Name) and
                node.func.id == 'super' and
                len(node.args) == 2 and
                all(isinstance(arg, ast.Name) for arg in node.args) and
                node.args[0].id == self._class_info_stack[-1].name and
                node.args[1].id == self._class_info_stack[-1].first_arg_name
        ):
            self.super_calls[_ast_to_offset(node)] = node
        elif (
                isinstance(node.func, ast.Name) and
                node.func.id == 'str' and
                len(node.args) == 1 and
                isinstance(node.args[0], ast.Str) and
                not node.keywords and
                not _starargs(node)
        ):
            self.native_literals.add(_ast_to_offset(node))

        self.generic_visit(node)