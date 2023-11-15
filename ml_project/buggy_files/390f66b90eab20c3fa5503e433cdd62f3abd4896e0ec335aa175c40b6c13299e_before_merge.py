    def visit_Call(self, node):  # type: (ast.Call) -> None
        if (
                isinstance(node.func, ast.Name) and
                node.func.id in {'isinstance', 'issubclass'} and
                len(node.args) == 2 and
                self._is_six(node.args[1], SIX_TYPE_CTX_ATTRS)
        ):
            arg = node.args[1]
            # _is_six() enforces this
            assert isinstance(arg, (ast.Name, ast.Attribute))
            self.six_type_ctx[_ast_to_offset(node.args[1])] = arg
        elif self._is_six(node.func, ('b',)):
            self.six_b.add(_ast_to_offset(node))
        elif self._is_six(node.func, SIX_CALLS) and not _starargs(node):
            self.six_calls[_ast_to_offset(node)] = node
        elif (
                isinstance(node.func, ast.Name) and
                node.func.id == 'next' and
                not _starargs(node) and
                isinstance(node.args[0], ast.Call) and
                self._is_six(
                    node.args[0].func,
                    ('iteritems', 'iterkeys', 'itervalues'),
                ) and
                not _starargs(node.args[0])
        ):
            self.six_iter[_ast_to_offset(node.args[0])] = node.args[0]
        elif (
                isinstance(self._previous_node, ast.Expr) and
                self._is_six(node.func, SIX_RAISES) and
                not _starargs(node)
        ):
            self.six_raises[_ast_to_offset(node)] = node
        elif (
                not self._in_comp and
                self._class_info_stack and
                self._class_info_stack[-1].def_depth == 1 and
                isinstance(node.func, ast.Name) and
                node.func.id == 'super' and
                len(node.args) == 2 and
                isinstance(node.args[0], ast.Name) and
                isinstance(node.args[1], ast.Name) and
                node.args[0].id == self._class_info_stack[-1].name and
                node.args[1].id == self._class_info_stack[-1].first_arg_name
        ):
            self.super_calls[_ast_to_offset(node)] = node
        elif (
                isinstance(node.func, ast.Name) and
                node.func.id == 'str' and
                not node.keywords and
                not _starargs(node) and
                (
                    len(node.args) == 0 or
                    (
                        len(node.args) == 1 and
                        isinstance(node.args[0], ast.Str)
                    )
                )
        ):
            self.native_literals.add(_ast_to_offset(node))
        elif (
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Str) and
                node.func.attr == 'encode' and
                not _starargs(node) and
                len(node.args) == 1 and
                isinstance(node.args[0], ast.Str) and
                _is_codec(node.args[0].s, 'utf-8')
        ):
            self.encode_calls[_ast_to_offset(node)] = node
        elif self._is_io_open(node.func):
            self.io_open_calls[_ast_to_offset(node)] = node

        self.generic_visit(node)