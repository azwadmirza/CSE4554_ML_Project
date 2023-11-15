    def __init__(self, native, modname, qualname, unique_name, doc,
                 typemap, restype, calltypes, args, kws, mangler=None,
                 argtypes=None, inline=False, noalias=False, env_name=None,
                 global_dict=None):
        self.native = native
        self.modname = modname
        self.global_dict = global_dict
        self.qualname = qualname
        self.unique_name = unique_name
        self.doc = doc
        # XXX typemap and calltypes should be on the compile result,
        # not the FunctionDescriptor
        self.typemap = typemap
        self.calltypes = calltypes
        self.args = args
        self.kws = kws
        self.restype = restype
        # Argument types
        if argtypes is not None:
            assert isinstance(argtypes, tuple), argtypes
            self.argtypes = argtypes
        else:
            # Get argument types from the type inference result
            # (note the "arg.FOO" convention as used in typeinfer
            self.argtypes = tuple(self.typemap['arg.' + a] for a in args)
        mangler = default_mangler if mangler is None else mangler
        # The mangled name *must* be unique, else the wrong function can
        # be chosen at link time.
        qualprefix = qualifying_prefix(self.modname, self.unique_name)
        self.mangled_name = mangler(qualprefix, self.argtypes)
        if env_name is None:
            env_name = mangler(".NumbaEnv.{}".format(qualprefix),
                               self.argtypes)
        self.env_name = env_name
        self.inline = inline
        self.noalias = noalias