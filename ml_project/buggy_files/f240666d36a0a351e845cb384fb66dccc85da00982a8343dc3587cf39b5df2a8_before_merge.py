    def op_BEGIN_FINALLY(self, inst, state):
        "no-op"
        none = ir.Const(None, loc=self.loc)
        self.store(value=none, name=state)