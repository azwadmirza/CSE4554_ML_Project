    def p_factor_unary(self, p):
        """factor : PLUS factor
                  | MINUS factor
                  | TILDE factor
        """
        op = self._factor_ops[p[1]]()
        p[0] = ast.UnaryOp(op=op, operand=p[2], lineno=self.lineno, col_offset=self.col)