    def visit_lambda_expr(self, e: LambdaExpr) -> Type:
        """Type check lambda expression."""
        inferred_type, type_override = self.infer_lambda_type_using_context(e)
        if not inferred_type:
            # No useful type context.
            ret_type = self.accept(e.expr(), allow_none_return=True)
            fallback = self.named_type('builtins.function')
            return callable_type(e, fallback, ret_type)
        else:
            # Type context available.
            self.chk.check_func_item(e, type_override=type_override)
            if e.expr() not in self.chk.type_map:
                self.accept(e.expr(), allow_none_return=True)
            ret_type = self.chk.type_map[e.expr()]
            if isinstance(ret_type, NoneTyp):
                # For "lambda ...: None", just use type from the context.
                # Important when the context is Callable[..., None] which
                # really means Void. See #1425.
                return inferred_type
            return replace_callable_return_type(inferred_type, ret_type)