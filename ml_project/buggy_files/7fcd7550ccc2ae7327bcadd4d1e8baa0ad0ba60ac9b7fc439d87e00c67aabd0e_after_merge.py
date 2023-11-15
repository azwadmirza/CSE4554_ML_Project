def macro_exceptions(module, macro_tree, compiler=None):
    try:
        yield
    except HyLanguageError as e:
        # These are user-level Hy errors occurring in the macro.
        # We want to pass them up to the user.
        reraise(type(e), e, sys.exc_info()[2])
    except Exception as e:

        if compiler:
            filename = compiler.filename
            source = compiler.source
        else:
            filename = None
            source = None

        exc_msg = '  '.join(traceback.format_exception_only(
            sys.exc_info()[0], sys.exc_info()[1]))

        msg = "expanding macro {}\n  ".format(str(macro_tree[0]))
        msg += exc_msg

        reraise(HyMacroExpansionError,
                HyMacroExpansionError(
                    msg, macro_tree, filename, source),
                sys.exc_info()[2])