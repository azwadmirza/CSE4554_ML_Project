    def check_lvalue(self, lvalue: Lvalue) -> Tuple[Optional[Type],
                                                    Optional[IndexExpr],
                                                    Optional[Var]]:
        lvalue_type = None  # type: Optional[Type]
        index_lvalue = None  # type: Optional[IndexExpr]
        inferred = None  # type: Optional[Var]

        if self.is_definition(lvalue):
            if isinstance(lvalue, NameExpr):
                inferred = cast(Var, lvalue.node)
                assert isinstance(inferred, Var)
            else:
                assert isinstance(lvalue, MemberExpr)
                self.expr_checker.accept(lvalue.expr)
                inferred = lvalue.def_var
        elif isinstance(lvalue, IndexExpr):
            index_lvalue = lvalue
        elif isinstance(lvalue, MemberExpr):
            lvalue_type = self.expr_checker.analyze_ordinary_member_access(lvalue,
                                                                 True)
            self.store_type(lvalue, lvalue_type)
        elif isinstance(lvalue, NameExpr):
            lvalue_type = self.expr_checker.analyze_ref_expr(lvalue, lvalue=True)
            self.store_type(lvalue, lvalue_type)
        elif isinstance(lvalue, TupleExpr) or isinstance(lvalue, ListExpr):
            types = [self.check_lvalue(sub_expr)[0] or
                     # This type will be used as a context for further inference of rvalue,
                     # we put Uninhabited if there is no information available from lvalue.
                     UninhabitedType() for sub_expr in lvalue.items]
            lvalue_type = TupleType(types, self.named_type('builtins.tuple'))
        else:
            lvalue_type = self.expr_checker.accept(lvalue)

        return lvalue_type, index_lvalue, inferred