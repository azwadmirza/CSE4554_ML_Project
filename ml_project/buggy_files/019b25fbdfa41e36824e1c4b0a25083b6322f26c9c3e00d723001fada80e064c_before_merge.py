    def visit_tuple_expr(self, e: TupleExpr) -> Type:
        """Type check a tuple expression."""
        ctx = None  # type: TupleType
        # Try to determine type context for type inference.
        if isinstance(self.chk.type_context[-1], TupleType):
            t = self.chk.type_context[-1]
            if len(t.items) == len(e.items):
                ctx = t
        # Infer item types.
        items = []  # type: List[Type]
        for i in range(len(e.items)):
            item = e.items[i]
            tt = None  # type: Type
            if not ctx:
                tt = self.accept(item)
            else:
                tt = self.accept(item, ctx.items[i])
            self.check_not_void(tt, e)
            items.append(tt)
        fallback_item = join.join_type_list(items)
        return TupleType(items, self.chk.named_generic_type('builtins.tuple', [fallback_item]))