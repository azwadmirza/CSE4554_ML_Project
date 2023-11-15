    def stage_inline_pass(self):
        """
        Inline calls to locally defined closures.
        """
        # Ensure we have an IR and type information.
        assert self.func_ir
        inline_pass = InlineClosureCallPass(self.func_ir, self.flags, run_frontend)
        inline_pass.run()
        # Remove all Dels, and re-run postproc
        post_proc = postproc.PostProcessor(self.func_ir)
        post_proc.run()

        if config.DEBUG or config.DUMP_IR:
            name = self.func_ir.func_id.func_qualname
            print(("IR DUMP: %s" % name).center(80, "-"))
            self.func_ir.dump()