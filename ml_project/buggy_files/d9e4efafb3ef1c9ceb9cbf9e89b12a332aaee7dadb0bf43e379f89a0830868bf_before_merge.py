    def visit_lambda_expr(self, e: LambdaExpr) -> Type:
        """Type check lambda expression."""
        self.chk.check_default_args(e, body_is_trivial=False)
        inferred_type, type_override = self.infer_lambda_type_using_context(e)
        if not inferred_type:
            self.chk.return_types.append(AnyType(TypeOfAny.special_form))
            # Type check everything in the body except for the final return
            # statement (it can contain tuple unpacking before return).
            for stmt in e.body.body[:-1]:
                stmt.accept(self.chk)
            # Only type check the return expression, not the return statement.
            # This is important as otherwise the following statements would be
            # considered unreachable. There's no useful type context.
            ret_type = self.accept(e.expr(), allow_none_return=True)
            fallback = self.named_type('builtins.function')
            self.chk.return_types.pop()
            return callable_type(e, fallback, ret_type)
        else:
            # Type context available.
            self.chk.return_types.append(inferred_type.ret_type)
            self.chk.check_func_item(e, type_override=type_override)
            if e.expr() not in self.chk.type_map:
                self.accept(e.expr(), allow_none_return=True)
            ret_type = self.chk.type_map[e.expr()]
            if isinstance(get_proper_type(ret_type), NoneType):
                # For "lambda ...: None", just use type from the context.
                # Important when the context is Callable[..., None] which
                # really means Void. See #1425.
                self.chk.return_types.pop()
                return inferred_type
            self.chk.return_types.pop()
            return replace_callable_return_type(inferred_type, ret_type)