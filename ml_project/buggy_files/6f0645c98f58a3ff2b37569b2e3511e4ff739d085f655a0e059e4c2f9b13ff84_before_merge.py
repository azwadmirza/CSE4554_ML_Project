def require(source_module, target_module, assignments, prefix=""):
    """Load macros from one module into the namespace of another.

    This function is called from the `require` special form in the compiler.

    Parameters
    ----------
    source_module: str or types.ModuleType
        The module from which macros are to be imported.

    target_module: str, types.ModuleType or None
        The module into which the macros will be loaded.  If `None`, then
        the caller's namespace.
        The latter is useful during evaluation of generated AST/bytecode.

    assignments: str or list of tuples of strs
        The string "ALL" or a list of macro name and alias pairs.

    prefix: str, optional ("")
        If nonempty, its value is prepended to the name of each imported macro.
        This allows one to emulate namespaced macros, like
        "mymacromodule.mymacro", which looks like an attribute of a module.

    Returns
    -------
    out: boolean
        Whether or not macros and tags were actually transferred.
    """

    if target_module is None:
        parent_frame = inspect.stack()[1][0]
        target_namespace = parent_frame.f_globals
        target_module = target_namespace.get('__name__', None)
    elif isinstance(target_module, string_types):
        target_module = importlib.import_module(target_module)
        target_namespace = target_module.__dict__
    elif inspect.ismodule(target_module):
        target_namespace = target_module.__dict__
    else:
        raise TypeError('`target_module` is not a recognized type: {}'.format(
            type(target_module)))

    # Let's do a quick check to make sure the source module isn't actually
    # the module being compiled (e.g. when `runpy` executes a module's code
    # in `__main__`).
    # We use the module's underlying filename for this (when they exist), since
    # it's the most "fixed" attribute.
    if _same_modules(source_module, target_module):
        return False

    if not inspect.ismodule(source_module):
        source_module = importlib.import_module(source_module)

    source_macros = source_module.__dict__.setdefault('__macros__', {})
    source_tags = source_module.__dict__.setdefault('__tags__', {})

    if len(source_module.__macros__) + len(source_module.__tags__) == 0:
        if assignments != "ALL":
            raise ImportError('The module {} has no macros or tags'.format(
                source_module))
        else:
            return False

    target_macros = target_namespace.setdefault('__macros__', {})
    target_tags = target_namespace.setdefault('__tags__', {})

    if prefix:
        prefix += "."

    if assignments == "ALL":
        name_assigns = [(k, k) for k in
            tuple(source_macros.keys()) + tuple(source_tags.keys())]
    else:
        name_assigns = assignments

    for name, alias in name_assigns:
        _name = mangle(name)
        alias = mangle(prefix + alias)
        if _name in source_module.__macros__:
            target_macros[alias] = source_macros[_name]
        elif _name in source_module.__tags__:
            target_tags[alias] = source_tags[_name]
        else:
            raise ImportError('Could not require name {} from {}'.format(
                _name, source_module))

    return True