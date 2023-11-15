    def _compile_maths_expression(self, expression):
        ops = {"+": ast.Add,
               "/": ast.Div,
               "//": ast.FloorDiv,
               "*": ast.Mult,
               "-": ast.Sub,
               "%": ast.Mod,
               "**": ast.Pow,
               "<<": ast.LShift,
               ">>": ast.RShift,
               "|": ast.BitOr,
               "^": ast.BitXor,
               "&": ast.BitAnd}
        if PY35:
            ops.update({"@": ast.MatMult})

        op = ops[expression.pop(0)]
        right_associative = op == ast.Pow

        lineno, col_offset = expression.start_line, expression.start_column
        if right_associative:
            expression = expression[::-1]
        ret = self.compile(expression.pop(0))
        for child in expression:
            left_expr = ret.force_expr
            ret += self.compile(child)
            right_expr = ret.force_expr
            if right_associative:
                left_expr, right_expr = right_expr, left_expr
            ret += ast.BinOp(left=left_expr,
                             op=op(),
                             right=right_expr,
                             lineno=lineno,
                             col_offset=col_offset)
        return ret