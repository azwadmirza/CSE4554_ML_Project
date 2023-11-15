    def _from_python_function(cls, func_ir, typemap, restype, calltypes,
                              native, mangler=None, inline=False, noalias=False):
        (qualname, unique_name, modname, doc, args, kws,
         )= cls._get_function_info(func_ir)
        self = cls(native, modname, qualname, unique_name, doc,
                   typemap, restype, calltypes,
                   args, kws, mangler=mangler, inline=inline, noalias=noalias)
        return self