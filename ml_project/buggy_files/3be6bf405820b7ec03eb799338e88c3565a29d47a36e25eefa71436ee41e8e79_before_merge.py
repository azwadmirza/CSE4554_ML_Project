    def try_subproc_toks(self, node, strip_expr=False):
        """Tries to parse the line of the node as a subprocess."""
        line, nlogical, idx = get_logical_line(self.lines, node.lineno - 1)
        if self.mode == "eval":
            mincol = len(line) - len(line.lstrip())
            maxcol = None
        else:
            mincol = max(min_col(node) - 1, 0)
            maxcol = max_col(node)
            if mincol == maxcol:
                maxcol = find_next_break(line, mincol=mincol, lexer=self.parser.lexer)
            elif nlogical > 1:
                maxcol = None
            elif maxcol < len(line) and line[maxcol] == ";":
                pass
            else:
                maxcol += 1
        spline = subproc_toks(
            line,
            mincol=mincol,
            maxcol=maxcol,
            returnline=False,
            lexer=self.parser.lexer,
        )
        if spline is None or len(spline) < len(line[mincol:maxcol]) + 2:
            # failed to get something consistent, try greedy wrap
            # The +2 comes from "![]" being length 3, minus 1 since maxcol
            # is one beyond the total length for slicing
            spline = subproc_toks(
                line,
                mincol=mincol,
                maxcol=maxcol,
                returnline=False,
                lexer=self.parser.lexer,
                greedy=True,
            )
        if spline is None:
            return node
        try:
            newnode = self.parser.parse(
                spline,
                mode=self.mode,
                filename=self.filename,
                debug_level=(self.debug_level > 2),
            )
            newnode = newnode.body
            if not isinstance(newnode, AST):
                # take the first (and only) Expr
                newnode = newnode[0]
            increment_lineno(newnode, n=node.lineno - 1)
            newnode.col_offset = node.col_offset
            if self.debug_level > 1:
                msg = "{0}:{1}:{2}{3} - {4}\n" "{0}:{1}:{2}{3} + {5}"
                mstr = "" if maxcol is None else ":" + str(maxcol)
                msg = msg.format(self.filename, node.lineno, mincol, mstr, line, spline)
                print(msg, file=sys.stderr)
        except SyntaxError:
            newnode = node
        if strip_expr and isinstance(newnode, Expr):
            newnode = newnode.value
        return newnode