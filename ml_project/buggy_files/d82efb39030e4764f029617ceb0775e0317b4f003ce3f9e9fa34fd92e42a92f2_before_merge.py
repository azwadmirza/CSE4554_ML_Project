    def check_multi_assignment(self, lvalues: List[Lvalue],
                               rvalue: Expression,
                               context: Context,
                               infer_lvalue_type: bool = True,
                               msg: Optional[str] = None) -> None:
        """Check the assignment of one rvalue to a number of lvalues."""

        # Infer the type of an ordinary rvalue expression.
        rvalue_type = self.expr_checker.accept(rvalue)  # TODO maybe elsewhere; redundant
        undefined_rvalue = False

        if isinstance(rvalue_type, UnionType):
            # If this is an Optional type in non-strict Optional code, unwrap it.
            relevant_items = rvalue_type.relevant_items()
            if len(relevant_items) == 1:
                rvalue_type = relevant_items[0]

        if isinstance(rvalue_type, AnyType):
            for lv in lvalues:
                if isinstance(lv, StarExpr):
                    lv = lv.expr
                temp_node = self.temp_node(AnyType(TypeOfAny.from_another_any,
                                                   source_any=rvalue_type), context)
                self.check_assignment(lv, temp_node, infer_lvalue_type)
        elif isinstance(rvalue_type, TupleType):
            self.check_multi_assignment_from_tuple(lvalues, rvalue, rvalue_type,
                                                   context, undefined_rvalue, infer_lvalue_type)
        else:
            self.check_multi_assignment_from_iterable(lvalues, rvalue_type,
                                                      context, infer_lvalue_type)