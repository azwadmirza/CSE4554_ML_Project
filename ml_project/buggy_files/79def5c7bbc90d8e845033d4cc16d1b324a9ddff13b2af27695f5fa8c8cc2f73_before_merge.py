    def check_assignment(self, lvalue: Node, rvalue: Node, infer_lvalue_type: bool = True) -> None:
        """Type check a single assignment: lvalue = rvalue."""
        if isinstance(lvalue, TupleExpr) or isinstance(lvalue, ListExpr):
            ltuple = cast(Union[TupleExpr, ListExpr], lvalue)

            self.check_assignment_to_multiple_lvalues(ltuple.items, rvalue, lvalue,
                                                      infer_lvalue_type)
        else:
            lvalue_type, index_lvalue, inferred = self.check_lvalue(lvalue)
            if lvalue_type:
                if isinstance(lvalue_type, PartialType) and lvalue_type.type is None:
                    # Try to infer a proper type for a variable with a partial None type.
                    rvalue_type = self.accept(rvalue)
                    if isinstance(rvalue_type, NoneTyp):
                        # This doesn't actually provide any additional information -- multiple
                        # None initializers preserve the partial None type.
                        return
                    if is_valid_inferred_type(rvalue_type):
                        lvalue_type.var.type = rvalue_type
                        partial_types = self.partial_types[-1]
                        del partial_types[lvalue_type.var]
                    # Try to infer a partial type. No need to check the return value, as
                    # an error will be reported elsewhere.
                    self.infer_partial_type(lvalue_type.var, lvalue, rvalue_type)
                    return
                rvalue_type = self.check_simple_assignment(lvalue_type, rvalue, lvalue)

                if rvalue_type and infer_lvalue_type:
                    self.binder.assign_type(lvalue, rvalue_type,
                                            self.typing_mode_weak())
            elif index_lvalue:
                self.check_indexed_assignment(index_lvalue, rvalue, rvalue)

            if inferred:
                self.infer_variable_type(inferred, lvalue, self.accept(rvalue),
                                         rvalue)