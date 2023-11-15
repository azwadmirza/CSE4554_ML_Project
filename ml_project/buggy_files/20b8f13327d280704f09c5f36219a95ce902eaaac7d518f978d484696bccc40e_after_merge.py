def _fix_py3_plus(contents_text):
    try:
        ast_obj = ast_parse(contents_text)
    except SyntaxError:
        return contents_text

    visitor = FindPy3Plus()
    visitor.visit(ast_obj)

    if not any((
            visitor.bases_to_remove,
            visitor.native_literals,
            visitor.six_b,
            visitor.six_calls,
            visitor.six_raises,
            visitor.six_remove_decorators,
            visitor.six_simple,
            visitor.six_type_ctx,
            visitor.six_with_metaclass,
            visitor.super_calls,
    )):
        return contents_text

    try:
        tokens = src_to_tokens(contents_text)
    except tokenize.TokenError:  # pragma: no cover (bpo-2180)
        return contents_text

    def _replace(i, mapping, node):
        new_token = Token('CODE', _get_tmpl(mapping, node))
        if isinstance(node, ast.Name):
            tokens[i] = new_token
        else:
            j = i
            while tokens[j].src != node.attr:
                j += 1
            tokens[i:j + 1] = [new_token]

    for i, token in reversed_enumerate(tokens):
        if not token.src:
            continue
        elif token.offset in visitor.bases_to_remove:
            _remove_base_class(tokens, i)
        elif token.offset in visitor.six_type_ctx:
            _replace(i, SIX_TYPE_CTX_ATTRS, visitor.six_type_ctx[token.offset])
        elif token.offset in visitor.six_simple:
            _replace(i, SIX_SIMPLE_ATTRS, visitor.six_simple[token.offset])
        elif token.offset in visitor.six_remove_decorators:
            if tokens[i - 1].src == '@':
                end = i + 1
                while tokens[end].name != 'NEWLINE':
                    end += 1
                del tokens[i - 1:end + 1]
        elif token.offset in visitor.six_b:
            j = _find_open_paren(tokens, i)
            if (
                    tokens[j + 1].name == 'STRING' and
                    _is_ascii(tokens[j + 1].src) and
                    tokens[j + 2].src == ')'
            ):
                func_args, end = _parse_call_args(tokens, j)
                _replace_call(tokens, i, end, func_args, SIX_B_TMPL)
        elif token.offset in visitor.six_calls:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            node = visitor.six_calls[token.offset]
            template = _get_tmpl(SIX_CALLS, node.func)
            _replace_call(tokens, i, end, func_args, template)
        elif token.offset in visitor.six_raises:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            node = visitor.six_raises[token.offset]
            template = _get_tmpl(SIX_RAISES, node.func)
            _replace_call(tokens, i, end, func_args, template)
        elif token.offset in visitor.six_with_metaclass:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            if len(func_args) == 1:
                tmpl = WITH_METACLASS_NO_BASES_TMPL
            else:
                tmpl = WITH_METACLASS_BASES_TMPL
            _replace_call(tokens, i, end, func_args, tmpl)
        elif token.offset in visitor.super_calls:
            i = _find_open_paren(tokens, i)
            call = visitor.super_calls[token.offset]
            victims = _victims(tokens, i, call, gen=False)
            del tokens[victims.starts[0] + 1:victims.ends[-1]]
        elif token.offset in visitor.native_literals:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            if any(tok.name == 'NL' for tok in tokens[i:end]):
                continue
            _replace_call(tokens, i, end, func_args, '{args[0]}')

    return tokens_to_src(tokens)