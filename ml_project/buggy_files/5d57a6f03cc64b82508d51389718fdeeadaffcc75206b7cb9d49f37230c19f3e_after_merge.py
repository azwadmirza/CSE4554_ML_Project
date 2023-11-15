    def lex_indent(self) -> None:
        """Analyze whitespace chars at the beginning of a line (indents)."""
        s = self.match(self.indent_exp)
        while True:
            s = self.match(self.indent_exp)
            if s == '' or s[-1] not in self.comment_or_newline:
                break
            # Empty line (whitespace only or comment only).
            self.add_pre_whitespace(s[:-1])
            if s[-1] == '#':
                self.lex_comment()
            else:
                self.lex_break()
        indent = self.calc_indent(s)
        if indent == self.indents[-1]:
            # No change in indent: just whitespace.
            self.add_pre_whitespace(s)
        elif indent > self.indents[-1]:
            # An increased indent (new block).
            self.indents.append(indent)
            self.add_token(Indent(s))
        else:
            # Decreased indent (end of one or more blocks).
            pre = self.pre_whitespace
            self.pre_whitespace = ''
            while indent < self.indents[-1]:
                self.add_token(Dedent(''))
                self.indents.pop()
            self.pre_whitespace = pre
            self.add_pre_whitespace(s)
            if indent != self.indents[-1]:
                # Error: indent level does not match a previous indent level.
                self.add_token(LexError('', INVALID_DEDENT))