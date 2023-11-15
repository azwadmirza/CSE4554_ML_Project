    def visit_decorator(self, dec: Decorator) -> None:
        """Try to infer the type of the decorated function.

        This lets us resolve references to decorated functions during
        type checking when there are cyclic imports, as otherwise the
        type might not be available when we need it.

        This basically uses a simple special-purpose type inference
        engine just for decorators.
        """
        # Don't just call the super method since we don't unconditionally traverse the decorated
        # function.
        dec.var.accept(self)
        for decorator in dec.decorators:
            decorator.accept(self)
        if self.recurse_into_functions:
            dec.func.accept(self)
        if dec.var.is_property:
            # Decorators are expected to have a callable type (it's a little odd).
            if dec.func.type is None:
                dec.var.type = CallableType(
                    [AnyType(TypeOfAny.special_form)],
                    [ARG_POS],
                    [None],
                    AnyType(TypeOfAny.special_form),
                    self.builtin_type('function'),
                    name=dec.var.name())
            elif isinstance(dec.func.type, CallableType):
                dec.var.type = dec.func.type
                self.analyze(dec.var.type, dec.var)
            return
        decorator_preserves_type = True
        for expr in dec.decorators:
            preserve_type = False
            if isinstance(expr, RefExpr) and isinstance(expr.node, FuncDef):
                if expr.node.type and is_identity_signature(expr.node.type):
                    preserve_type = True
            if not preserve_type:
                decorator_preserves_type = False
                break
        if decorator_preserves_type:
            # No non-identity decorators left. We can trivially infer the type
            # of the function here.
            dec.var.type = function_type(dec.func, self.builtin_type('function'))
        if dec.decorators:
            return_type = calculate_return_type(dec.decorators[0])
            if return_type and isinstance(return_type, AnyType):
                # The outermost decorator will return Any so we know the type of the
                # decorated function.
                dec.var.type = AnyType(TypeOfAny.from_another_any, source_any=return_type)
            sig = find_fixed_callable_return(dec.decorators[0])
            if sig:
                # The outermost decorator always returns the same kind of function,
                # so we know that this is the type of the decoratored function.
                orig_sig = function_type(dec.func, self.builtin_type('function'))
                sig.name = orig_sig.items()[0].name
                dec.var.type = sig
        self.analyze(dec.var.type, dec.var)