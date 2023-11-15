def convert_macro_arg(raw_arg, kind, glbs, locs, *, name='<arg>',
                      macroname='<macro>'):
    """Converts a string macro argument based on the requested kind.

    Parameters
    ----------
    raw_arg : str
        The str reprensetaion of the macro argument.
    kind : object
        A flag or type representing how to convert the argument.
    glbs : Mapping
        The globals from the call site.
    locs : Mapping or None
        The locals from the call site.
    name : str, optional
        The macro argument name.
    macroname : str, optional
        The name of the macro itself.

    Returns
    -------
    The converted argument.
    """
    # munge kind and mode to start
    mode = None
    if isinstance(kind, cabc.Sequence) and not isinstance(kind, str):
        # have (kind, mode) tuple
        kind, mode = kind
    if isinstance(kind, str):
        kind = _convert_kind_flag(kind)
    if kind is str or kind is None:
        return raw_arg  # short circut since there is nothing else to do
    # select from kind and convert
    execer = builtins.__xonsh_execer__
    filename = macroname + '(' + name + ')'
    if kind is AST:
        ctx = set(dir(builtins)) | set(glbs.keys())
        if locs is not None:
            ctx |= set(locs.keys())
        mode = mode or 'eval'
        arg = execer.parse(raw_arg, ctx, mode=mode, filename=filename)
    elif kind is types.CodeType or kind is compile:
        mode = mode or 'eval'
        arg = execer.compile(raw_arg, mode=mode, glbs=glbs, locs=locs,
                             filename=filename)
    elif kind is eval:
        arg = execer.eval(raw_arg, glbs=glbs, locs=locs, filename=filename)
    elif kind is exec:
        mode = mode or 'exec'
        if not raw_arg.endswith('\n'):
            raw_arg += '\n'
        arg = execer.exec(raw_arg, mode=mode, glbs=glbs, locs=locs,
                          filename=filename)
    elif kind is type:
        arg = type(execer.eval(raw_arg, glbs=glbs, locs=locs,
                               filename=filename))
    else:
        msg = ('kind={0!r} and mode={1!r} was not recongnized for macro '
               'argument {2!r}')
        raise TypeError(msg.format(kind, mode, name))
    return arg