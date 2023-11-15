    def visit_tuple_expr(self, e: TupleExpr) -> Type:
        """Type check a tuple expression."""
        ctx = None  # type: TupleType
        # Try to determine type context for type inference.
        if isinstance(self.chk.type_context[-1], TupleType):
            t = self.chk.type_context[-1]
            ctx = t
        # NOTE: it's possible for the context to have a different
        # number of items than e.  In that case we use those context
        # items that match a position in e, and we'll worry about type
        # mismatches later.

        # Infer item types.  Give up if there's a star expression
        # that's not a Tuple.
        items = []  # type: List[Type]
        j = 0  # Index into ctx.items; irrelevant if ctx is None.
        for i in range(len(e.items)):
            item = e.items[i]
            tt = None  # type: Type
            if isinstance(item, StarExpr):
                # Special handling for star expressions.
                # TODO: If there's a context, and item.expr is a
                # TupleExpr, flatten it, so we can benefit from the
                # context?  Counterargument: Why would anyone write
                # (1, *(2, 3)) instead of (1, 2, 3) except in a test?
                tt = self.accept(item.expr)
                self.check_not_void(tt, e)
                if isinstance(tt, TupleType):
                    items.extend(tt.items)
                    j += len(tt.items)
                else:
                    # A star expression that's not a Tuple.
                    # Treat the whole thing as a variable-length tuple.
                    return self.check_lst_expr(e.items, 'builtins.tuple', '<tuple>', e)
            else:
                if not ctx or j >= len(ctx.items):
                    tt = self.accept(item)
                else:
                    tt = self.accept(item, ctx.items[j])
                    j += 1
                self.check_not_void(tt, e)
                items.append(tt)
        fallback_item = join.join_type_list(items)
        return TupleType(items, self.chk.named_generic_type('builtins.tuple', [fallback_item]))