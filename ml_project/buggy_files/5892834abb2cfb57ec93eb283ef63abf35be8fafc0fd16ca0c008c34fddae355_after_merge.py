    def _analyze_op_build_tuple(self, scope, equiv_set, expr):
        # For the moment, we can't do anything with tuples that
        # contain arrays, compared to array dimensions.  Return
        # None to say we won't track this tuple if a part of it
        # is an array.
        for x in expr.items:
            if (
                isinstance(x, ir.Var)
                and isinstance(self.typemap[x.name], types.ArrayCompatible)
            ):
                return None

        consts = []
        for var in expr.items:
            x = guard(find_const, self.func_ir, var)
            if x is not None:
                consts.append(x)
            else:
                break
        else:
            out = tuple([ir.Const(x, expr.loc) for x in consts])
            return out, [], ir.Const(tuple(consts), expr.loc)
        # default return for non-const
        return tuple(expr.items), []