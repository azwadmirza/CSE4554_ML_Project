    def try_infer_partial_type_from_indexed_assignment(
            self, lvalue: IndexExpr, rvalue: Node) -> None:
        # TODO: Should we share some of this with try_infer_partial_type?
        if isinstance(lvalue.base, RefExpr):
            var = cast(Var, lvalue.base.node)
            partial_types = self.find_partial_types(var)
            if partial_types is not None:
                typename = cast(Instance, var.type).type.fullname()
                if typename == 'builtins.dict':
                    # TODO: Don't infer things twice.
                    key_type = self.accept(lvalue.index)
                    value_type = self.accept(rvalue)
                    if is_valid_inferred_type(key_type) and is_valid_inferred_type(value_type):
                        var.type = self.named_generic_type('builtins.dict', [key_type, value_type])
                        del partial_types[var]