    def op_COMPARE_OP(self, inst, lhs, rhs, res):
        op = dis.cmp_op[inst.arg]
        if op == 'in' or op == 'not in':
            lhs, rhs = rhs, lhs

        if op == 'not in':
            self._binop('in', lhs, rhs, res)
            tmp = self.get(res)
            out = ir.Expr.unary('not', value=tmp, loc=self.loc)
            self.store(out, res)
        elif op == 'exception match':
            gv_fn = ir.Global(
                "exception_match", eh.exception_match, loc=self.loc,
            )
            exc_match_name = '$exc_match'
            self.store(value=gv_fn, name=exc_match_name, redefine=True)
            lhs = self.get(lhs)
            rhs = self.get(rhs)
            exc = ir.Expr.call(
                self.get(exc_match_name), args=(lhs, rhs), kws=(), loc=self.loc,
            )
            self.store(exc, res)
        else:
            self._binop(op, lhs, rhs, res)