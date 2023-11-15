    def run(self):
        """Run a trace over the bytecode over all reachable path.

        The trace starts at bytecode offset 0 and gathers stack and control-
        flow information by partially interpreting each bytecode.
        Each ``State`` instance in the trace corresponds to a basic-block.
        The State instances forks when a jump instruction is encountered.
        A newly forked state is then added to the list of pending states.
        The trace ends when there are no more pending states.
        """
        firststate = State(bytecode=self._bytecode, pc=0, nstack=0,
                           blockstack=())
        runner = TraceRunner(debug_filename=self._bytecode.func_id.filename)
        runner.pending.append(firststate)

        # Enforce unique-ness on initial PC to avoid re-entering the PC with
        # a different stack-depth. We don't know if such a case is ever
        # possible, but no such case has been encountered in our tests.
        first_encounter = UniqueDict()
        # Loop over each pending state at a initial PC.
        # Each state is tracing a basic block
        while runner.pending:
            _logger.debug("pending: %s", runner.pending)
            state = runner.pending.popleft()
            if state not in runner.finished:
                _logger.debug("stack: %s", state._stack)
                first_encounter[state.pc_initial] = state
                # Loop over the state until it is terminated.
                while True:
                    runner.dispatch(state)
                    # Terminated?
                    if state.has_terminated():
                        break
                    elif (state.has_active_try() and
                            state.get_inst().opname not in _NO_RAISE_OPS):
                        # Is in a *try* block
                        state.fork(pc=state.get_inst().next)
                        tryblk = state.get_top_block('TRY')
                        state.pop_block_and_above(tryblk)
                        nstack = state.stack_depth
                        kwargs = {}
                        if nstack > tryblk['entry_stack']:
                            kwargs['npop'] = nstack - tryblk['entry_stack']
                        handler = tryblk['handler']
                        kwargs['npush'] = {
                            BlockKind('EXCEPT'): _EXCEPT_STACK_OFFSET,
                            BlockKind('FINALLY'): _FINALLY_POP
                        }[handler['kind']]
                        kwargs['extra_block'] = handler
                        state.fork(pc=tryblk['end'], **kwargs)
                        break
                    else:
                        state.advance_pc()
                        # Must the new PC be a new block?
                        if self._is_implicit_new_block(state):
                            state.split_new_block()
                            break
                _logger.debug("end state. edges=%s", state.outgoing_edges)
                runner.finished.add(state)
                out_states = state.get_outgoing_states()
                runner.pending.extend(out_states)

        # Complete controlflow
        self._build_cfg(runner.finished)
        # Prune redundant PHI-nodes
        self._prune_phis(runner)
        # Post process
        for state in sorted(runner.finished, key=lambda x: x.pc_initial):
            self.block_infos[state.pc_initial] = si = adapt_state_infos(state)
            _logger.debug("block_infos %s:\n%s", state, si)