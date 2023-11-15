def macroexpand(tree, module, compiler=None, once=False):
    """Expand the toplevel macros for the given Hy AST tree.

    Load the macros from the given `module`, then expand the (top-level) macros
    in `tree` until we no longer can.

    `HyExpression` resulting from macro expansions are assigned the module in
    which the macro function is defined (determined using `inspect.getmodule`).
    If the resulting `HyExpression` is itself macro expanded, then the
    namespace of the assigned module is checked first for a macro corresponding
    to the expression's head/car symbol.  If the head/car symbol of such a
    `HyExpression` is not found among the macros of its assigned module's
    namespace, the outer-most namespace--e.g.  the one given by the `module`
    parameter--is used as a fallback.

    Parameters
    ----------
    tree: HyObject or list
        Hy AST tree.

    module: str or types.ModuleType
        Module used to determine the local namespace for macros.

    compiler: HyASTCompiler, optional
        The compiler object passed to expanded macros.

    once: boolean, optional
        Only expand the first macro in `tree`.

    Returns
    ------
    out: HyObject
        Returns a mutated tree with macros expanded.
    """
    if not inspect.ismodule(module):
        module = importlib.import_module(module)

    assert not compiler or compiler.module == module

    while True:

        if not isinstance(tree, HyExpression) or tree == []:
            break

        fn = tree[0]
        if fn in ("quote", "quasiquote") or not isinstance(fn, HySymbol):
            break

        fn = mangle(fn)
        expr_modules = (([] if not hasattr(tree, 'module') else [tree.module])
            + [module])

        # Choose the first namespace with the macro.
        m = next((mod.__macros__[fn]
                  for mod in expr_modules
                  if fn in mod.__macros__),
                 None)
        if not m:
            break

        opts = {}
        if m._hy_macro_pass_compiler:
            if compiler is None:
                from hy.compiler import HyASTCompiler
                compiler = HyASTCompiler(module)
            opts['compiler'] = compiler

        with macro_exceptions(module, tree, compiler):
            obj = m(module.__name__, *tree[1:], **opts)

            if isinstance(obj, HyExpression):
                obj.module = inspect.getmodule(m)

            tree = replace_hy_obj(obj, tree)

        if once:
            break

    tree = wrap_value(tree)
    return tree