def has_shell(context):
    keywords = context.node.keywords
    result = False
    if 'shell' in context.call_keywords:
        for key in keywords:
            if key.arg == 'shell':
                val = key.value
                if isinstance(val, ast.Num):
                    result = bool(val.n)
                elif isinstance(val, ast.List):
                    result = bool(val.elts)
                elif isinstance(val, ast.Dict):
                    result = bool(val.keys)
                elif isinstance(val, ast.Name) and val.id in ['False', 'None']:
                    result = False
                elif not six.PY2 and isinstance(val, ast.NameConstant):
                    result = val.value
                else:
                    result = True
    return result