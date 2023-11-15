    def _make_table_aliases(self, expr):
        ctx = self.context
        node = expr.op()
        if isinstance(node, ops.Join):
            for arg in node.args:
                if isinstance(arg, ir.TableExpr):
                    self._make_table_aliases(arg)
        else:
            if not ctx.is_extracted(expr):
                ctx.make_alias(expr)
            else:
                # The compiler will apply a prefix only if the current context
                # contains two or more table references. So, if we've extracted
                # a subquery into a CTE, we need to propagate that reference
                # down to child contexts so that they aren't missing any refs.
                ctx.set_ref(expr, ctx.top_context.get_ref(expr))