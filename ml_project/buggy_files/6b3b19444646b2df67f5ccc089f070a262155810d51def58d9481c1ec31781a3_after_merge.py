    def gen_explicit_neg(self, arg, arg_rel, arg_typ, size_typ, loc, scope,
                         dsize, stmts, equiv_set):
        assert(not isinstance(size_typ, int))
        # Create var to hold the calculated slice size.
        explicit_neg_var = ir.Var(scope, mk_unique_var("explicit_neg"), loc)
        explicit_neg_val = ir.Expr.binop(operator.add, dsize, arg, loc=loc)
        # Determine the type of that var.  Can be literal if we know the
        # literal size of the dimension.
        explicit_neg_typ = types.intp
        self.calltypes[explicit_neg_val] = signature(explicit_neg_typ,
                                                     size_typ, arg_typ)
        # We'll prepend this slice size calculation to the get/setitem.
        stmts.append(ir.Assign(value=explicit_neg_val,
                               target=explicit_neg_var, loc=loc))
        self._define(equiv_set, explicit_neg_var,
                     explicit_neg_typ, explicit_neg_val)
        return explicit_neg_var, explicit_neg_typ