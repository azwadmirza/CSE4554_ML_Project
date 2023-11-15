def _to_fstring(src, call):
    params = {}
    for i, arg in enumerate(call.args):
        params[str(i)] = _unparse(arg)
    for kwd in call.keywords:
        params[kwd.arg] = _unparse(kwd.value)

    parts = []
    i = 0
    for s, name, spec, conv in parse_format('f' + src):
        if name is not None:
            k, dot, rest = name.partition('.')
            name = ''.join((params[k or str(i)], dot, rest))
            i += 1
        parts.append((s, name, spec, conv))
    return unparse_parsed_string(parts)