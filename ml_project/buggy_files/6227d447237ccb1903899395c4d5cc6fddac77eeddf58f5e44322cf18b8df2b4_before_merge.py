    def try_infer_partial_type_from_indexed_assignment(
            self, lvalue: IndexExpr, rvalue: Node) -> None:
        # TODO: Should we share some of this with try_infer_partial_type?
        partial_types = self.partial_types[-1]
        if not partial_types:
            # Fast path leave -- no partial types in the current scope.
            return
        if isinstance(lvalue.base, RefExpr):
            var = lvalue.base.node
            if var in partial_types:
                var = cast(Var, var)
                typename = cast(Instance, var.type).type.fullname()
                if typename == 'builtins.dict':
                    # TODO: Don't infer things twice.
                    key_type = self.accept(lvalue.index)
                    value_type = self.accept(rvalue)
                    if is_valid_inferred_type(key_type) and is_valid_inferred_type(value_type):
                        var.type = self.named_generic_type('builtins.dict', [key_type, value_type])
                        del partial_types[var]