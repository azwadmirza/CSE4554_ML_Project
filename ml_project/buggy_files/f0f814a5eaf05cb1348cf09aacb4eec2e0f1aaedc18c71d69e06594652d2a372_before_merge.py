    def _compile_core(self):
        """
        Populate and run compiler pipeline
        """
        pm = _PipelineManager()

        if not self.flags.force_pyobject:
            pm.create_pipeline("nopython")
            if self.func_ir is None:
                pm.add_stage(self.stage_analyze_bytecode, "analyzing bytecode")
            pm.add_stage(self.stage_process_ir, "processing IR")
            if not self.flags.no_rewrites:
                pm.add_stage(self.stage_generic_rewrites, "nopython rewrites")
            pm.add_stage(self.stage_nopython_frontend, "nopython frontend")
            pm.add_stage(self.stage_annotate_type, "annotate type")
            if not self.flags.no_rewrites:
                pm.add_stage(self.stage_nopython_rewrites, "nopython rewrites")
            pm.add_stage(self.stage_nopython_backend, "nopython mode backend")
            pm.add_stage(self.stage_cleanup, "cleanup intermediate results")

        if self.status.can_fallback or self.flags.force_pyobject:
            pm.create_pipeline("object")
            if self.func_ir is None:
                pm.add_stage(self.stage_analyze_bytecode, "analyzing bytecode")
            pm.add_stage(self.stage_process_ir, "processing IR")
            pm.add_stage(self.stage_objectmode_frontend, "object mode frontend")
            pm.add_stage(self.stage_annotate_type, "annotate type")
            pm.add_stage(self.stage_objectmode_backend, "object mode backend")
            pm.add_stage(self.stage_cleanup, "cleanup intermediate results")

        if self.status.can_giveup:
            pm.create_pipeline("interp")
            pm.add_stage(self.stage_compile_interp_mode, "compiling with interpreter mode")
            pm.add_stage(self.stage_cleanup, "cleanup intermediate results")

        pm.finalize()
        res = pm.run(self.status)
        if res is not None:
            # Early pipeline completion
            return res
        else:
            assert self.cr is not None
            return self.cr