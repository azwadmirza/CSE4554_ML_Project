    def p_string_literal(self, p):
        """string_literal : string_tok"""
        p1 = p[1]
        prefix = RE_STRINGPREFIX.match(p1.value).group()
        if "p" in prefix:
            value_without_p = prefix.replace("p", "") + p1.value[len(prefix) :]
            s = ast.Str(
                s=ast.literal_eval(value_without_p),
                lineno=p1.lineno,
                col_offset=p1.lexpos,
            )
            p[0] = xonsh_call(
                "__xonsh_path_literal__", [s], lineno=p1.lineno, col=p1.lexpos
            )
        elif "f" in prefix or "F" in prefix:
            s = pyparse(p1.value).body[0].value
            s = ast.increment_lineno(s, p1.lineno - 1)
            p[0] = s
        else:
            s = ast.literal_eval(p1.value)
            is_bytes = "b" in prefix or "B" in prefix
            cls = ast.Bytes if is_bytes else ast.Str
            p[0] = cls(s=s, lineno=p1.lineno, col_offset=p1.lexpos)