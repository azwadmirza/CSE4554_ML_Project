def handle_name(state, token):
    """Function for handling name tokens"""
    typ = "NAME"
    if state["pymode"][-1][0]:
        if token.string in kwmod.kwlist:
            typ = token.string.upper()
        state["last"] = token
        yield _new_token(typ, token.string, token.start)
    else:
        prev = state["last"]
        state["last"] = token
        has_whitespace = prev.end != token.start
        if token.string == "and" and has_whitespace:
            yield _new_token("AND", token.string, token.start)
        elif token.string == "or" and has_whitespace:
            yield _new_token("OR", token.string, token.start)
        else:
            yield _new_token("NAME", token.string, token.start)