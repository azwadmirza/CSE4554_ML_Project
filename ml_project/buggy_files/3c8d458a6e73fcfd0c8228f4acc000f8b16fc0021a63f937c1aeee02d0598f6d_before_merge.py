    def _get_successors(self, job):
        """
        Get a collection of successors out of the current job.

        :param CFGJob job:  The CFGJob instance.
        :return:            A collection of successors.
        :rtype:             list
        """

        addr = job.addr
        sim_successors = job.sim_successors
        cfg_node = job.cfg_node
        input_state = job.state
        func_addr = job.func_addr

        # check step limit
        if self._max_steps is not None:
            depth = cfg_node.depth
            if depth >= self._max_steps:
                return [ ]

        successors = [ ]
        is_indirect_jump = sim_successors.sort == 'IRSB' and self._is_indirect_jump(cfg_node, sim_successors)
        indirect_jump_resolved_by_resolvers = False

        if is_indirect_jump and self._resolve_indirect_jumps:
            # Try to resolve indirect jumps
            irsb = input_state.block().vex

            resolved, resolved_targets, ij = self._indirect_jump_encountered(addr, cfg_node, irsb, func_addr,
                                                                             stmt_idx=DEFAULT_STATEMENT)
            if resolved:
                successors = self._convert_indirect_jump_targets_to_states(job, resolved_targets)
                if ij:
                    self._indirect_jump_resolved(ij, ij.addr, None, resolved_targets)
            else:
                # Try to resolve this indirect jump using heavier approaches
                resolved_targets = self._process_one_indirect_jump(ij)
                successors = self._convert_indirect_jump_targets_to_states(job, resolved_targets)

            if successors:
                indirect_jump_resolved_by_resolvers = True
            else:
                # It's unresolved. Add it to the wait list (but apparently we don't have any better way to resolve it
                # right now).
                self._indirect_jumps_to_resolve.add(ij)

        if not successors:
            # Get all successors of this block
            successors = (sim_successors.flat_successors + sim_successors.unsat_successors) \
                if addr not in self._avoid_runs else []

        # Post-process successors
        successors, job.extra_info = self._post_process_successors(input_state, sim_successors, successors)

        all_successors = successors + sim_successors.unconstrained_successors

        # make sure FakeRets are at the last
        all_successors = [ suc for suc in all_successors if suc.history.jumpkind != 'Ijk_FakeRet' ] + \
                         [ suc for suc in all_successors if suc.history.jumpkind == 'Ijk_FakeRet' ]

        if self._keep_state:
            cfg_node.final_states = all_successors[::]

        if is_indirect_jump and not indirect_jump_resolved_by_resolvers:
            # For indirect jumps, filter successors that do not make sense
            successors = self._filter_insane_successors(successors)

        successors = self._try_resolving_indirect_jumps(sim_successors,
                                                        cfg_node,
                                                        func_addr,
                                                        successors,
                                                        job.exception_info,
                                                        self._block_artifacts)
        # Remove all successors whose IP is symbolic
        successors = [ s for s in successors if not s.ip.symbolic ]

        # Add additional edges supplied by the user
        successors = self._add_additional_edges(input_state, sim_successors, cfg_node, successors)

        # if base graph is used, add successors implied from the graph
        if self._base_graph:
            basegraph_successor_addrs = set()
            for src_, dst_ in self._base_graph.edges():
                if src_.addr == addr:
                    basegraph_successor_addrs.add(dst_.addr)
            successor_addrs = {s.solver.eval(s.ip) for s in successors}
            extra_successor_addrs = basegraph_successor_addrs - successor_addrs

            if all_successors:  # make sure we have a base state to use
                base_state = all_successors[0]  # TODO: for calls, we want to use the fake_ret state

                for s_addr in extra_successor_addrs:
                    # an extra target
                    successor_state = base_state.copy()
                    successor_state.ip = s_addr
                    successors.append(successor_state)
            else:
                if extra_successor_addrs:
                    l.error('CFGEmulated terminates at %#x although base graph provided more exits.', addr)

        if not successors:
            # There is no way out :-(
            # Log it first
            self._push_unresolvable_run(addr)

            if sim_successors.sort == 'SimProcedure' and isinstance(sim_successors.artifacts['procedure'],
                    SIM_PROCEDURES["stubs"]["PathTerminator"]):
                # If there is no valid exit in this branch and it's not
                # intentional (e.g. caused by a SimProcedure that does not
                # do_return) , we should make it return to its call-site. However,
                # we don't want to use its state anymore as it might be corrupted.
                # Just create an edge in the graph.
                return_target = job.call_stack.current_return_target
                if return_target is not None:
                    new_call_stack = job.call_stack_copy()
                    return_target_key = self._generate_block_id(
                        new_call_stack.stack_suffix(self.context_sensitivity_level),
                        return_target,
                        False
                    )  # You can never return to a syscall

                    if not cfg_node.instruction_addrs:
                        ret_ins_addr = None
                    else:
                        if self.project.arch.branch_delay_slot:
                            if len(cfg_node.instruction_addrs) > 1:
                                ret_ins_addr = cfg_node.instruction_addrs[-2]
                            else:
                                l.error('At %s: expecting more than one instruction. Only got one.', cfg_node)
                                ret_ins_addr = None
                        else:
                            ret_ins_addr = cfg_node.instruction_addrs[-1]

                    # Things might be a bit difficult here. _graph_add_edge() requires both nodes to exist, but here
                    # the return target node may not exist yet. If that's the case, we will put it into a "delayed edge
                    # list", and add this edge later when the return target CFGNode is created.
                    if return_target_key in self._nodes:
                        self._graph_add_edge(job.block_id, return_target_key, jumpkind='Ijk_Ret',
                                             stmt_id=DEFAULT_STATEMENT, ins_addr=ret_ins_addr)
                    else:
                        self._pending_edges[return_target_key].append((job.block_id, return_target_key,
                                                                       {
                                                                           'jumpkind': 'Ijk_Ret',
                                                                           'stmt_id': DEFAULT_STATEMENT,
                                                                           'ins_addr': ret_ins_addr,
                                                                        }
                                                                       )
                                                                      )

            else:
                # There are no successors, but we still want to update the function graph
                artifacts = job.sim_successors.artifacts
                if 'irsb' in artifacts and 'insn_addrs' in artifacts and artifacts['insn_addrs']:
                    the_irsb = artifacts['irsb']
                    insn_addrs = artifacts['insn_addrs']
                    self._handle_job_without_successors(job, the_irsb, insn_addrs)

        # TODO: replace it with a DDG-based function IO analysis
        # handle all actions
        if successors:
            self._handle_actions(successors[0],
                                 sim_successors,
                                 job.current_function,
                                 job.current_stack_pointer,
                                 set(),
                                 )

        return successors