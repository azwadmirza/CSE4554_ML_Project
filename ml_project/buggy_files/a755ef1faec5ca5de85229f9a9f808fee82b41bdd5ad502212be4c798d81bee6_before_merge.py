def error_handler(state, token):
    tokentype = token.gettokentype()
    if tokentype == '$end':
        source_pos = token.source_pos or token.getsourcepos()
        source = state.source
        if source_pos:
            lineno = source_pos.lineno
            colno = source_pos.colno
        else:
            lineno = -1
            colno = -1

        raise PrematureEndOfInput.from_lexer("Premature end of input", state,
                                             token)
    else:
        raise LexException.from_lexer(
            "Ran into a %s where it wasn't expected." % tokentype, state,
            token)