    def p_factor_unary(self, p):
        """factor : plus_tok factor
                  | minus_tok factor
                  | tilde_tok factor
        """
        p1 = p[1]
        op = self._factor_ops[p1.value]()
        p[0] = ast.UnaryOp(
            op=op, operand=p[2], lineno=self.lineno, col_offset=p1.lexpos
        )