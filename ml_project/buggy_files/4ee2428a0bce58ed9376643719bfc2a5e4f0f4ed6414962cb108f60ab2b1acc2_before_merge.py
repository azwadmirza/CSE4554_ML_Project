def _fix_fstrings(contents_text):
    try:
        ast_obj = ast_parse(contents_text)
    except SyntaxError:
        return contents_text

    visitor = FindSimpleFormats()
    visitor.visit(ast_obj)

    if not visitor.found:
        return contents_text

    tokens = src_to_tokens(contents_text)
    for i, token in reversed_enumerate(tokens):
        node = visitor.found.get(token.offset)
        if node is None:
            continue

        if _is_bytestring(token.src):  # pragma: no cover (py2-only)
            continue

        paren = i + 3
        if tokens_to_src(tokens[i + 1:paren + 1]) != '.format(':
            continue

        # we don't actually care about arg position, so we pass `node`
        victims = _victims(tokens, paren, node, gen=False)
        end = victims.ends[-1]
        # if it spans more than one line, bail
        if tokens[end].line != token.line:
            continue

        tokens[i] = token._replace(src=_to_fstring(token.src, node))
        del tokens[i + 1:end + 1]

    return tokens_to_src(tokens)