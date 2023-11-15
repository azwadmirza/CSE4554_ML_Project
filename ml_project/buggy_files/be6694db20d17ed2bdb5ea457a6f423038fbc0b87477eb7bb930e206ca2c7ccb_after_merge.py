    def compile_list_comprehension(self, expr):
        # (list-comp expr (target iter) cond?)
        expr.pop(0)
        expression = expr.pop(0)
        gen_gen = expr[0]

        if not isinstance(gen_gen, HyList):
            raise HyTypeError(gen_gen, "Generator expression must be a list.")

        gen_res, gen = self._compile_generator_iterables(expr)

        if len(gen) == 0:
            raise HyTypeError(gen_gen, "Generator expression cannot be empty.")

        compiled_expression = self.compile(expression)
        ret = compiled_expression + gen_res
        ret += ast.ListComp(
            lineno=expr.start_line,
            col_offset=expr.start_column,
            elt=compiled_expression.force_expr,
            generators=gen)

        return ret