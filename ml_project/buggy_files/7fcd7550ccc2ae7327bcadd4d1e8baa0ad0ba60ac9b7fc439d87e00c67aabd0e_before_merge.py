def macro_exceptions(module, macro_tree, compiler=None):
    try:
        yield
    except Exception as e:
        try:
            filename = inspect.getsourcefile(module)
            source = inspect.getsource(module)
        except TypeError:
            if compiler:
                filename = compiler.filename
                source = compiler.source

        if not isinstance(e, HyTypeError):
            exc_type = HyMacroExpansionError
            msg = "expanding `{}': ".format(macro_tree[0])
            msg += str(e).replace("<lambda>()", "", 1).strip()
        else:
            exc_type = HyTypeError
            msg = e.message

        reraise(exc_type,
                exc_type(msg, filename, macro_tree, source),
                sys.exc_info()[2].tb_next)