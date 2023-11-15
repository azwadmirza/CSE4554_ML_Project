    def compile_comprehension(self, expr, root, parts, final):
        root = unmangle(ast_str(root))
        node_class = {
            "for":  asty.For,
            "lfor": asty.ListComp,
            "dfor": asty.DictComp,
            "sfor": asty.SetComp,
            "gfor": asty.GeneratorExp}[root]
        is_for = root == "for"

        orel = []
        if is_for:
            # Get the `else`.
            body, else_expr = final
            if else_expr is not None:
                orel.append(self._compile_branch(else_expr))
                orel[0] += orel[0].expr_as_stmt()
        else:
            # Get the final value (and for dictionary
            # comprehensions, the final key).
            if node_class is asty.DictComp:
                key, elt = map(self.compile, final)
            else:
                key = None
                elt = self.compile(final)

        # Compile the parts.
        if is_for:
            parts = parts[0]
        if not parts:
            return Result(expr=ast.parse({
                asty.For: "None",
                asty.ListComp: "[]",
                asty.DictComp: "{}",
                asty.SetComp: "{1}.__class__()",
                asty.GeneratorExp: "(_ for _ in [])"}[node_class]).body[0].value)
        parts = [
            Tag(p.tag, self.compile(p.value) if p.tag in ["if", "do"] else [
                self._storeize(p.value[0], self.compile(p.value[0])),
                self.compile(p.value[1])])
            for p in parts]

        # Produce a result.
        if (is_for or elt.stmts or (key is not None and key.stmts) or
            any(p.tag == 'do' or (p.value[1].stmts if p.tag in ("for", "afor", "setv") else p.value.stmts)
                for p in parts)):
            # The desired comprehension can't be expressed as a
            # real Python comprehension. We'll write it as a nested
            # loop in a function instead.
            contains_yield = []
            def f(parts):
                # This function is called recursively to construct
                # the nested loop.
                if not parts:
                    if is_for:
                        if body:
                            bd = self._compile_branch(body)
                            if bd.contains_yield:
                                contains_yield.append(True)
                            return bd + bd.expr_as_stmt()
                        return Result(stmts=[asty.Pass(expr)])
                    if node_class is asty.DictComp:
                        ret = key + elt
                        val = asty.Tuple(
                            key, ctx=ast.Load(),
                            elts=[key.force_expr, elt.force_expr])
                    else:
                        ret = elt
                        val = elt.force_expr
                    return ret + asty.Expr(
                        elt, value=asty.Yield(elt, value=val))
                (tagname, v), parts = parts[0], parts[1:]
                if tagname in ("for", "afor"):
                    orelse = orel and orel.pop().stmts
                    node = asty.AsyncFor if tagname == "afor" else asty.For
                    return v[1] + node(
                        v[1], target=v[0], iter=v[1].force_expr, body=f(parts).stmts,
                        orelse=orelse)
                elif tagname == "setv":
                    return v[1] + asty.Assign(
                        v[1], targets=[v[0]], value=v[1].force_expr) + f(parts)
                elif tagname == "if":
                    return v + asty.If(
                        v, test=v.force_expr, body=f(parts).stmts, orelse=[])
                elif tagname == "do":
                    return v + v.expr_as_stmt() + f(parts)
                else:
                    raise ValueError("can't happen")
            if is_for:
                ret = f(parts)
                ret.contains_yield = bool(contains_yield)
                return ret
            fname = self.get_anon_var()
            # Define the generator function.
            ret = Result() + asty.FunctionDef(
                expr,
                name=fname,
                args=ast.arguments(
                    args=[], vararg=None, kwarg=None,
                    kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=f(parts).stmts,
                decorator_list=[])
            # Immediately call the new function. Unless the user asked
            # for a generator, wrap the call in `[].__class__(...)` or
            # `{}.__class__(...)` or `{1}.__class__(...)` to get the
            # right type. We don't want to just use e.g. `list(...)`
            # because the name `list` might be rebound.
            return ret + Result(expr=ast.parse(
                "{}({}())".format(
                    {asty.ListComp: "[].__class__",
                     asty.DictComp: "{}.__class__",
                     asty.SetComp: "{1}.__class__",
                     asty.GeneratorExp: ""}[node_class],
                    fname)).body[0].value)

        # We can produce a real comprehension.
        generators = []
        for tagname, v in parts:
            if tagname in ("for", "afor"):
                generators.append(ast.comprehension(
                    target=v[0], iter=v[1].expr, ifs=[],
                    is_async=int(tagname == "afor")))
            elif tagname == "setv":
                generators.append(ast.comprehension(
                    target=v[0],
                    iter=asty.Tuple(v[1], elts=[v[1].expr], ctx=ast.Load()),
                    ifs=[], is_async=0))
            elif tagname == "if":
                generators[-1].ifs.append(v.expr)
            else:
                raise ValueError("can't happen")
        if node_class is asty.DictComp:
            return asty.DictComp(expr, key=key.expr, value=elt.expr, generators=generators)
        return node_class(expr, elt=elt.expr, generators=generators)