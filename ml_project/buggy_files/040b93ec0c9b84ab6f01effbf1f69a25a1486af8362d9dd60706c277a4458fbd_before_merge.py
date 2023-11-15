def parse(code):
    class_names, code = pre_parse(code)
    o = ast.parse(code)  # python ast
    decorate_ast(o, code, class_names)  # decorated python ast
    o = resolve_negative_literals(o)
    return o.body