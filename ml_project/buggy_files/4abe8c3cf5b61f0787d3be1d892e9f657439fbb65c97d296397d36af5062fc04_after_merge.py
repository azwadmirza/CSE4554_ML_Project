    def _handle_CCall(self, expr):
        if not isinstance(expr.args[0], pyvex.IRExpr.Const):
            return
        cond_type_enum = expr.args[0].con.value

        if self.arch.name in { 'X86', 'AMD64', 'AARCH64' }:
            if cond_type_enum in EXPECTED_COND_TYPES[self.arch.name]:
                self._handle_Comparison(expr.args[2], expr.args[3])
        elif is_arm_arch(self.arch):
            if cond_type_enum in EXPECTED_COND_TYPES['ARM']:
                self._handle_Comparison(expr.args[2], expr.args[3])
        else:
            raise ValueError("Unexpected ccall encountered in architecture %s." % self.arch.name)