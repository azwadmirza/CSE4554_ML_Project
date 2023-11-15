    def stage_inline_pass(self):
        """
        Inline calls to locally defined closures.
        """
        # Ensure we have an IR and type information.
        assert self.func_ir

        # if the return type is a pyobject, there's no type info available and
        # no ability to resolve certain typed function calls in the array
        # inlining code, use this variable to indicate
        typed_pass = not isinstance(self.return_type, types.misc.PyObject)
        inline_pass = InlineClosureCallPass(self.func_ir,
                                            self.flags.auto_parallel,
                                            self.parfor_diagnostics.replaced_fns,
                                            typed_pass)
        inline_pass.run()
        # Remove all Dels, and re-run postproc
        post_proc = postproc.PostProcessor(self.func_ir)
        post_proc.run()

        if config.DEBUG or config.DUMP_IR:
            name = self.func_ir.func_id.func_qualname
            print(("IR DUMP: %s" % name).center(80, "-"))
            self.func_ir.dump()