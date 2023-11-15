    def _(fn):
        fn = rename_function(fn, name)
        try:
            fn._hy_macro_pass_compiler = has_kwargs(fn)
        except Exception:
            # An exception might be raised if fn has arguments with
            # names that are invalid in Python.
            fn._hy_macro_pass_compiler = False

        module = inspect.getmodule(fn)
        module_macros = module.__dict__.setdefault('__macros__', {})
        module_macros[name] = fn

        return fn