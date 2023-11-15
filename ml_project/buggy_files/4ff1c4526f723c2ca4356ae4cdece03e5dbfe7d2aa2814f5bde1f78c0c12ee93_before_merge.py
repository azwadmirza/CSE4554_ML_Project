    def printf(self, format, *args):
        """
        Inspired from numba/cgutils.py

        Calls printf().
        Argument `format` is expected to be a Python string.
        Values to be printed are listed in `args`.

        Note: There is no checking to ensure there is correct number of values
        in `args` and there type matches the declaration in the format string.
        """
        assert isinstance(format, str)
        mod = self.mod
        # Make global constant for format string
        cstring = llvm_ir.IntType(8).as_pointer()
        fmt_bytes = self.make_bytearray((format + '\00').encode('ascii'))

        base_name = "printf_format"
        count = 0
        while self.mod.get_global("%s_%d" % (base_name, count)):
            count += 1
        global_fmt = self.global_constant("%s_%d" % (base_name, count),
                                          fmt_bytes)
        fnty = llvm_ir.FunctionType(llvm_ir.IntType(32), [cstring],
                                    var_arg=True)
        # Insert printf()
        fn = mod.get_global('printf')
        if fn is None:
            fn = llvm_ir.Function(mod, fnty, name="printf")
        # Call
        ptr_fmt = self.builder.bitcast(global_fmt, cstring)
        return self.builder.call(fn, [ptr_fmt] + list(args))