    def visit_Call(self, node):  # type: (ast.Call) -> None
        if (
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Str) and
                node.func.attr == 'format' and
                all(_simple_arg(arg) for arg in node.args) and
                all(_simple_arg(k.value) for k in node.keywords) and
                not _starargs(node)
        ):
            seen = set()
            for _, name, spec, _ in parse_format(node.func.value.s):
                # timid: difficult to rewrite correctly
                if spec is not None and '{' in spec:
                    break
                if name is not None:
                    candidate, _, _ = name.partition('.')
                    # timid: could make the f-string longer
                    if candidate and candidate in seen:
                        break
                    # timid: bracketed
                    elif '[' in candidate:
                        break
                    seen.add(candidate)
            else:
                self.found[_ast_to_offset(node)] = node

        self.generic_visit(node)