def parse(code):
    class_names, code = pre_parse(code)
    if '\x00' in code:
        raise ParserException('No null bytes (\\x00) allowed in the source code.')
    o = ast.parse(code)  # python ast
    decorate_ast(o, code, class_names)  # decorated python ast
    o = resolve_negative_literals(o)
    return o.body