    def _get_function_info(cls, func_ir):
        """
        Returns
        -------
        qualname, unique_name, modname, doc, args, kws, globals

        ``unique_name`` must be a unique name.
        """
        func = func_ir.func_id.func
        qualname = func_ir.func_id.func_qualname
        # XXX to func_id
        modname = func.__module__
        doc = func.__doc__ or ''
        args = tuple(func_ir.arg_names)
        kws = ()        # TODO
        global_dict = None

        if modname is None:
            # Dynamically generated function.
            modname = _dynamic_modname
            # Retain a reference to the dictionary of the function.
            # This disables caching, serialization and pickling.
            global_dict = func_ir.func_id.func.__globals__

        unique_name = func_ir.func_id.unique_name

        return qualname, unique_name, modname, doc, args, kws, global_dict