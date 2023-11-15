    def _runPass(self, index, pss, internal_state):
        mutated = False

        def check(func, compiler_state):
            mangled = func(compiler_state)
            if mangled not in (True, False):
                msg = ("CompilerPass implementations should return True/False. "
                       "CompilerPass with name '%s' did not.")
                raise ValueError(msg % pss.name())
            return mangled

        # wire in the analysis info so it's accessible
        pss.analysis = self._analysis

        with SimpleTimer() as init_time:
            mutated |= check(pss.run_initialization, internal_state)
        with SimpleTimer() as pass_time:
            mutated |= check(pss.run_pass, internal_state)
        with SimpleTimer() as finalize_time:
            mutated |= check(pss.run_finalizer, internal_state)

        if self._ENFORCING:
            # TODO: Add in self consistency enforcement for
            # `func_ir._definitions` etc
            if _pass_registry.get(pss.__class__).mutates_CFG:
                if mutated: # block level changes, rebuild all
                    PostProcessor(internal_state.func_ir).run()
                else: # CFG level changes rebuild CFG
                    internal_state.func_ir.blocks = transforms.canonicalize_cfg(
                        internal_state.func_ir.blocks)

        # inject runtimes
        pt = pass_timings(init_time.elapsed, pass_time.elapsed,
                          finalize_time.elapsed)
        self.exec_times["%s_%s" % (index, pss.name())] = pt

        # debug print after this pass?
        if pss.name() in self._print_after:
            fid = internal_state.func_id
            args = (fid.modname, fid.func_qualname, self.pipeline_name,
                    pss.name())
            print(("%s.%s: %s: %s" % args).center(80, '-'))
            internal_state.func_ir.dump()