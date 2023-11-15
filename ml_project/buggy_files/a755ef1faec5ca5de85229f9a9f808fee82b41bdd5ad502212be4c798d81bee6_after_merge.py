def error_handler(state, token):
    tokentype = token.gettokentype()
    if tokentype == '$end':
        raise PrematureEndOfInput.from_lexer("Premature end of input", state,
                                             token)
    else:
        raise LexException.from_lexer(
            "Ran into a %s where it wasn't expected." % tokentype, state,
            token)