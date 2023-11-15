    def interpret(self, bytecode):
        """
        Generate IR for this bytecode.
        """
        self.bytecode = bytecode

        self.scopes = []
        global_scope = ir.Scope(parent=None, loc=self.loc)
        self.scopes.append(global_scope)

        if PYVERSION < (3, 7):
            # Control flow analysis
            self.cfa = controlflow.ControlFlowAnalysis(bytecode)
            self.cfa.run()
            if config.DUMP_CFG:
                self.cfa.dump()

            # Data flow analysis
            self.dfa = dataflow.DataFlowAnalysis(self.cfa)
            self.dfa.run()
        else:
            flow = Flow(bytecode)
            flow.run()
            self.dfa = AdaptDFA(flow)
            self.cfa = AdaptCFA(flow)
            if config.DUMP_CFG:
                self.cfa.dump()

        # Temp states during interpretation
        self.current_block = None
        self.current_block_offset = None
        self.syntax_blocks = []
        self.dfainfo = None

        firstblk = min(self.cfa.blocks.keys())
        self.scopes.append(ir.Scope(parent=self.current_scope, loc=self.loc))
        # Interpret loop
        for inst, kws in self._iter_inst():
            self._dispatch(inst, kws)

        self._legalize_exception_vars()

        # Prepare FunctionIR
        fir = ir.FunctionIR(self.blocks, self.is_generator, self.func_id,
                             self.first_loc, self.definitions,
                             self.arg_count, self.arg_names)
        _logger.debug(fir.dump_to_string())
        return fir