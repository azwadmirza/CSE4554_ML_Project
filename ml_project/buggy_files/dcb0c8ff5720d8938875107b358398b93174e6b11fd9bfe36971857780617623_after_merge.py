    def op_LOAD_CONST(self, inst, res):
        value = self.code_consts[inst.arg]
        if isinstance(value, tuple):
            st = []
            for x in value:
                nm = '$const_%s' % str(x)
                val_const = ir.Const(x, loc=self.loc)
                target = self.store(val_const, name=nm, redefine=True)
                st.append(target)
            const = ir.Expr.build_tuple(st, loc=self.loc)
        else:
            const = ir.Const(value, loc=self.loc)
        self.store(const, res)