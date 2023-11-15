    def try_infer_partial_type_from_indexed_assignment(
            self, lvalue: IndexExpr, rvalue: Node) -> None:
        # TODO: Should we share some of this with try_infer_partial_type?
        if isinstance(lvalue.base, RefExpr):
            var = cast(Var, lvalue.base.node)
            if var is not None and isinstance(var.type, PartialType):
                type_type = var.type.type
                if type_type is None:
                    return  # The partial type is None.
                partial_types = self.find_partial_types(var)
                if partial_types is None:
                    return
                typename = type_type.fullname()
                if typename == 'builtins.dict':
                    # TODO: Don't infer things twice.
                    key_type = self.accept(lvalue.index)
                    value_type = self.accept(rvalue)
                    if is_valid_inferred_type(key_type) and is_valid_inferred_type(value_type):
                        if not self.current_node_deferred:
                            var.type = self.named_generic_type('builtins.dict',
                                                               [key_type, value_type])
                        del partial_types[var]