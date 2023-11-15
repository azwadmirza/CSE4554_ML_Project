    def p_del_stmt(self, p):
        """del_stmt : del_tok exprlist"""
        p1 = p[1]
        p2 = p[2]
        for targ in p2:
            targ.ctx = ast.Del()
        p0 = ast.Delete(targets=p2, lineno=p1.lineno, col_offset=p1.lexpos)
        p[0] = p0