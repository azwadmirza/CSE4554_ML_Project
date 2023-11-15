def can_compile(src):
    """Returns whether the code can be compiled, i.e. it is valid xonsh."""
    src = src if src.endswith('\n') else src + '\n'
    src = src.lstrip()
    try:
        builtins.__xonsh_execer__.compile(src, mode='single', glbs=None,
                                          locs=builtins.__xonsh_ctx__)
        rtn = True
    except SyntaxError:
        rtn = False
    return rtn