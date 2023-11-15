    def visit_func_expr(self, e: FuncExpr) -> Type:
        """Type check lambda expression."""
        inferred_type = self.infer_lambda_type_using_context(e)
        if not inferred_type:
            # No useful type context.
            ret_type = e.expr().accept(self.chk)
            if not e.arguments:
                # Form 'lambda: e'; just use the inferred return type.
                return CallableType([], [], [], ret_type, self.named_type('builtins.function'))
            else:
                # TODO: Consider reporting an error. However, this is fine if
                # we are just doing the first pass in contextual type
                # inference.
                return AnyType()
        else:
            # Type context available.
            self.chk.check_func_item(e, type_override=inferred_type)
            if e.expr() not in self.chk.type_map:
                self.accept(e.expr())
            ret_type = self.chk.type_map[e.expr()]
            return replace_callable_return_type(inferred_type, ret_type)