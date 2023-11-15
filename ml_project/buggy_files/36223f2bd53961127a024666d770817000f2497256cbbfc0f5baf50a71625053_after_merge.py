    def stage_objectmode_frontend(self):
        """
        Front-end: Analyze bytecode, generate Numba IR, infer types
        """
        self.func_ir = self.func_ir_original or self.func_ir
        if self.flags.enable_looplift:
            assert not self.lifted
            cres = self.frontend_looplift()
            if cres is not None:
                raise _EarlyPipelineCompletion(cres)

        # Fallback typing: everything is a python object
        self.typemap = defaultdict(lambda: types.pyobject)
        self.calltypes = defaultdict(lambda: types.pyobject)
        self.return_type = types.pyobject