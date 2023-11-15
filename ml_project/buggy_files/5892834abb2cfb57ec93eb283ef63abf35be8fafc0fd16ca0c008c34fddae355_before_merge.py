    def _analyze_op_build_tuple(self, scope, equiv_set, expr):
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