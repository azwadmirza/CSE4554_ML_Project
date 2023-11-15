    def visit_return_stmt(self, s: ReturnStmt) -> Type:
        """Type check a return statement."""
        self.binder.breaking_out = True
        if self.is_within_function():
            defn = self.function_stack[-1]
            if defn.is_generator:
                return_type = self.get_generator_return_type(self.return_types[-1],
                                                             defn.is_coroutine)
            else:
                return_type = self.return_types[-1]

            if s.expr:
                # Return with a value.
                typ = self.accept(s.expr, return_type)
                # Returning a value of type Any is always fine.
                if isinstance(typ, AnyType):
                    return None

                if self.is_unusable_type(return_type):
                    # Lambdas are allowed to have a unusable returns.
                    # Functions returning a value of type None are allowed to have a Void return.
                    if isinstance(self.function_stack[-1], FuncExpr) or isinstance(typ, NoneTyp):
                        return None
                    self.fail(messages.NO_RETURN_VALUE_EXPECTED, s)
                else:
                    self.check_subtype(
                        subtype_label='got',
                        subtype=typ,
                        supertype_label='expected',
                        supertype=return_type,
                        context=s,
                        msg=messages.INCOMPATIBLE_RETURN_VALUE_TYPE)
            else:
                # Empty returns are valid in Generators with Any typed returns.
                if (self.function_stack[-1].is_generator and isinstance(return_type, AnyType)):
                    return None

                if isinstance(return_type, (Void, NoneTyp, AnyType)):
                    return None

                if self.in_checked_function():
                    self.fail(messages.RETURN_VALUE_EXPECTED, s)