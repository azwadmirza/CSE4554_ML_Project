    def compile_list_comprehension(self, expr):
        # (list-comp expr (target iter) cond?)
        expr.pop(0)
        expression = expr.pop(0)

        gen_res, gen = self._compile_generator_iterables(expr)

        compiled_expression = self.compile(expression)
        ret = compiled_expression + gen_res
        ret += ast.ListComp(
            lineno=expr.start_line,
            col_offset=expr.start_column,
            elt=compiled_expression.force_expr,
            generators=gen)

        return ret