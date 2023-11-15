    def op_BEGIN_FINALLY(self, inst, temps):
        # The *temps* are the exception variables
        const_none = ir.Const(None, loc=self.loc)
        for tmp in temps:
            # Set to None for now
            self.store(const_none, name=tmp)
            self._exception_vars.add(tmp)