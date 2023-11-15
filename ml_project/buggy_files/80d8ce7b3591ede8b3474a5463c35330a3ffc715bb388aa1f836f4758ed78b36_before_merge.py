    def from_lexer(cls, message, state, token):
        source_pos = token.getsourcepos()
        if token.source_pos:
            lineno = source_pos.lineno
            colno = source_pos.colno
        else:
            lineno = -1
            colno = -1

        if state.source:
            lines = state.source.splitlines()
            if lines[-1] == '':
                del lines[-1]

            if lineno < 1:
                lineno = len(lines)
            if colno < 1:
                colno = len(lines[-1])

            source = lines[lineno - 1]
        return cls(message, state.filename, lineno, colno, source)