    def stage_parfor_pass(self):
        """
        Convert data-parallel computations into Parfor nodes
        """
        # Ensure we have an IR and type information.
        assert self.func_ir
        parfor_pass = ParforPass(self.func_ir, self.type_annotation.typemap,
            self.type_annotation.calltypes, self.return_type)
        parfor_pass.run()