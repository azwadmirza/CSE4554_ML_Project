    def _get_successors(self, job):
        # Extract initial values
        state = job.state
        addr = job.addr

        # Obtain successors
        if addr not in self._avoid_runs:
            all_successors = job.sim_successors.flat_successors + job.sim_successors.unconstrained_successors
        else:
            all_successors = []

        # save those states
        job.vfg_node.final_states = all_successors[:]

        # Update thumb_addrs
        if job.sim_successors.sort == 'IRSB' and state.thumb:
            self._thumb_addrs.update(job.sim_successors.artifacts['insn_addrs'])

        if len(all_successors) == 0:
            if job.sim_successors.sort == 'SimProcedure' and isinstance(job.sim_successors.artifacts['procedure'],
                    simuvex.procedures.SimProcedures["stubs"]["PathTerminator"]):
                # If there is no valid exit in this branch and it's not
                # intentional (e.g. caused by a SimProcedure that does not
                # do_return) , we should make it return to its callsite.
                # However, we don't want to use its state as it might be
                # corrupted. Just create a link in the exit_targets map.
                retn_target = job.call_stack.current_return_target
                if retn_target is not None:
                    new_call_stack = job.call_stack_copy()
                    exit_target_tpl = new_call_stack.stack_suffix(self._context_sensitivity_level) + (retn_target,)
                    self._exit_targets[job.call_stack_suffix + (addr,)].append(
                        (exit_target_tpl, 'Ijk_Ret'))
            else:
                # This is intentional. We shall remove all the pending returns generated before along this path.
                self._remove_pending_return(job, self._pending_returns)

        # If this is a call exit, we shouldn't put the default exit (which
        # is artificial) into the CFG. The exits will be Ijk_Call and
        # Ijk_FakeRet, and Ijk_Call always goes first
        job.is_call_jump = any([self._is_call_jumpkind(i.scratch.jumpkind) for i in all_successors])
        call_targets = [i.se.exactly_int(i.ip) for i in all_successors if self._is_call_jumpkind(i.scratch.jumpkind)]
        job.call_target = None if not call_targets else call_targets[0]

        job.is_return_jump = len(all_successors) and all_successors[0].scratch.jumpkind == 'Ijk_Ret'

        if job.is_call_jump:
            # create the call task

            # TODO: correctly fill the return address
            call_task = CallAnalysis(job.addr, None, [ ])
            self._task_stack.append(call_task)

            job.call_task = call_task

        return all_successors