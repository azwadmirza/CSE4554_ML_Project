def has_shell(context):
    keywords = context.node.keywords
    if 'shell' in context.call_keywords:
        for key in keywords:
            if key.arg == 'shell':
                val = key.value
                if isinstance(val, ast.Num):
                    return bool(val.n)
                if isinstance(val, ast.List):
                    return bool(val.elts)
                if isinstance(val, ast.Dict):
                    return bool(val.keys)
                if isinstance(val, ast.Name):
                    if val.id in ['False', 'None']:
                        return False
                return True
    return False