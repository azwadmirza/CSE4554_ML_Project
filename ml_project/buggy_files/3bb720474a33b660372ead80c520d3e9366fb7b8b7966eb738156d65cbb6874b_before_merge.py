def _fix_py2_compatible(contents_text):
    try:
        ast_obj = ast_parse(contents_text)
    except SyntaxError:
        return contents_text
    visitor = Py2CompatibleVisitor()
    visitor.visit(ast_obj)
    if not any((
            visitor.dicts,
            visitor.sets,
            visitor.set_empty_literals,
            visitor.is_literal,
    )):
        return contents_text

    tokens = src_to_tokens(contents_text)
    for i, token in reversed_enumerate(tokens):
        if token.offset in visitor.dicts:
            _process_dict_comp(tokens, i, visitor.dicts[token.offset])
        elif token.offset in visitor.set_empty_literals:
            _process_set_empty_literal(tokens, i)
        elif token.offset in visitor.sets:
            _process_set_literal(tokens, i, visitor.sets[token.offset])
        elif token.offset in visitor.is_literal:
            _process_is_literal(tokens, i, visitor.is_literal[token.offset])
    return tokens_to_src(tokens)