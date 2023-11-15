    def compile_comprehension(self, expr, form, expression, gen, cond):
        # (list-comp expr [target iter] cond?)

        if not isinstance(gen, HyList):
            raise HyTypeError(gen, "Generator expression must be a list.")

        gen_res, gen = self._compile_generator_iterables(
            [gen] + ([] if cond is None else [cond]))

        if len(gen) == 0:
            raise HyTypeError(expr, "Generator expression cannot be empty.")

        ret = self.compile(expression)
        node_class = (
            asty.ListComp if form == "list-comp" else
            asty.SetComp if form == "set-comp" else
            asty.GeneratorExp)
        return ret + gen_res + node_class(
            expr, elt=ret.force_expr, generators=gen)