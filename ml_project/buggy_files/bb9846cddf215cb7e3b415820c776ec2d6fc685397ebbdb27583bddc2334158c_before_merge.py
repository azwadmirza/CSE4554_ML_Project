    def _get_module_for_linking(self):
        """
        Internal: get a LLVM module suitable for linking multiple times
        into another library.  Exported functions are made "linkonce_odr"
        to allow for multiple definitions, inlining, and removal of
        unused exports.

        See discussion in https://github.com/numba/numba/pull/890
        """
        if self._shared_module is not None:
            return self._shared_module
        mod = self._final_module
        to_fix = []
        nfuncs = 0
        for fn in mod.functions:
            nfuncs += 1
            if not fn.is_declaration and fn.linkage == ll.Linkage.external:
                to_fix.append(fn.name)
        if nfuncs == 0:
            # This is an issue which can occur if loading a module
            # from an object file and trying to link with it, so detect it
            # here to make debugging easier.
            raise RuntimeError("library unfit for linking: "
                               "no available functions in %s"
                               % (self,))
        if to_fix:
            mod = mod.clone()
            for name in to_fix:
                # NOTE: this will mark the symbol WEAK if serialized
                # to an ELF file
                mod.get_function(name).linkage = 'linkonce_odr'
        self._shared_module = mod
        return mod