    def _compile_core(self):
        """
        Populate and run compiler pipeline
        """
        pms = self.define_pipelines()
        for pm in pms:
            pipeline_name = pm.pipeline_name
            func_name = "%s.%s" % (self.state.func_id.modname,
                                   self.state.func_id.func_qualname)

            event("Pipeline: %s for %s" % (pipeline_name, func_name))
            self.state.metadata['pipeline_times'] = {pipeline_name:
                                                     pm.exec_times}
            is_final_pipeline = pm == pms[-1]
            res = None
            try:
                pm.run(self.state)
                if self.state.cr is not None:
                    break
            except _EarlyPipelineCompletion as e:
                res = e.result
                break
            except Exception as e:
                self.state.status.fail_reason = e
                if is_final_pipeline:
                    raise e
        else:
            raise CompilerError("All available pipelines exhausted")

        # Pipeline is done, remove self reference to release refs to user code
        self.state.pipeline = None

        # organise a return
        if res is not None:
            # Early pipeline completion
            return res
        else:
            assert self.state.cr is not None
            return self.state.cr