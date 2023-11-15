def macroexpand_1(tree, compiler):
    """Expand the toplevel macro from `tree` once, in the context of
    `module_name`."""
    if isinstance(tree, HyExpression):
        if tree == []:
            return tree

        fn = tree[0]
        if fn in ("quote", "quasiquote"):
            return tree
        ntree = HyExpression(tree[:])
        ntree.replace(tree)

        opts = {}

        if isinstance(fn, HyString):
            m = _hy_macros[compiler.module_name].get(fn)
            if m is None:
                m = _hy_macros[None].get(fn)
            if m is not None:
                if m._hy_macro_pass_compiler:
                    opts['compiler'] = compiler

                try:
                    m_copy = make_empty_fn_copy(m)
                    m_copy(*ntree[1:], **opts)
                except TypeError as e:
                    msg = "expanding `" + str(tree[0]) + "': "
                    msg += str(e).replace("<lambda>()", "", 1).strip()
                    raise HyMacroExpansionError(tree, msg)

                try:
                    obj = wrap_value(m(*ntree[1:], **opts))
                except HyTypeError as e:
                    if e.expression is None:
                        e.expression = tree
                    raise
                except Exception as e:
                    msg = "expanding `" + str(tree[0]) + "': " + repr(e)
                    raise HyMacroExpansionError(tree, msg)
                replace_hy_obj(obj, tree)
                return obj
        return ntree
    return tree