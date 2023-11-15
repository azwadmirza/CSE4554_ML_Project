    def _create_job_call(self, addr, irsb, cfg_node, stmt_idx, ins_addr, current_function_addr, target_addr, jumpkind,
                         is_syscall=False):
        """
        Generate a CFGJob for target address, also adding to _pending_entries
        if returning to succeeding position (if irsb arg is populated)

        :param int addr:            Address of the predecessor node
        :param pyvex.IRSB irsb:     IRSB of the predecessor node
        :param CFGNode cfg_node:    The CFGNode instance of the predecessor node
        :param int stmt_idx:        ID of the source statement
        :param int ins_addr:        Address of the source instruction
        :param int current_function_addr: Address of the current function
        :param int target_addr:     Destination of the call
        :param str jumpkind:        The jumpkind of the edge going to this node
        :param bool is_syscall:     Is the jump kind (and thus this) a system call
        :return:                    A list of CFGJobs
        :rtype:                     list
        """

        jobs = [ ]

        if is_syscall:
            # Fix the target_addr for syscalls
            tmp_state = self.project.factory.blank_state(mode="fastpath", addr=cfg_node.addr)
            # Find the first successor with a syscall jumpkind
            successors = self._simulate_block_with_resilience(tmp_state)
            if successors is not None:
                succ = next(iter(succ for succ in successors.flat_successors
                                 if succ.history.jumpkind and succ.history.jumpkind.startswith("Ijk_Sys")), None)
            else:
                succ = None
            if succ is None:
                # For some reason, there is no such successor with a syscall jumpkind
                target_addr = self._unresolvable_call_target_addr
            else:
                try:
                    syscall_stub = self.project.simos.syscall(succ)
                    if syscall_stub:  # can be None if simos is not a subclass of SimUserspace
                        syscall_addr = syscall_stub.addr
                        target_addr = syscall_addr
                    else:
                        target_addr = self._unresolvable_call_target_addr
                except AngrUnsupportedSyscallError:
                    target_addr = self._unresolvable_call_target_addr

        if isinstance(target_addr, SootAddressDescriptor):
            new_function_addr = target_addr.method
        else:
            new_function_addr = target_addr

        if irsb is None:
            return_site = None
        else:
            if self.project.arch.name != 'Soot':
                return_site = addr + irsb.size  # We assume the program will always return to the succeeding position
            else:
                # For Soot, we return to the next statement, which is not necessarily the next block (as Shimple does
                # not break blocks at calls)
                assert isinstance(ins_addr, SootAddressDescriptor)
                soot_block = irsb
                return_block_idx = ins_addr.block_idx
                if stmt_idx + 1 >= soot_block.label + len(soot_block.statements):
                    # tick the block ID
                    return_block_idx += 1
                return_site = SootAddressDescriptor(ins_addr.method, return_block_idx, stmt_idx + 1)

        edge = None
        if new_function_addr is not None:
            edge = FunctionCallEdge(cfg_node, new_function_addr, return_site, current_function_addr, syscall=is_syscall,
                                    ins_addr=ins_addr, stmt_idx=stmt_idx,
                                    )

        if new_function_addr is not None:
            # Keep tracing from the call
            ce = CFGJob(target_addr, new_function_addr, jumpkind, last_addr=addr, src_node=cfg_node,
                        src_stmt_idx=stmt_idx, src_ins_addr=ins_addr, syscall=is_syscall, func_edges=[ edge ],
                        gp=self.kb.functions[current_function_addr].info.get('gp', None),
                        )
            jobs.append(ce)

        callee_might_return = True
        callee_function = None

        if new_function_addr is not None:
            if is_syscall or self.project.is_hooked(new_function_addr):
                # we can create the function if it is a syscall or a SimProcedure and it does not exist yet. Note that
                # syscalls are handled as SimProcedures anyway.
                callee_function = self.kb.functions.function(addr=new_function_addr, syscall=is_syscall, create=True)
            else:
                callee_function = self.kb.functions.function(addr=new_function_addr, syscall=is_syscall)
            if callee_function is not None:
                callee_might_return = not (callee_function.returning is False)

        if callee_might_return:
            func_edges = [ ]
            if return_site is not None:
                if callee_function is not None and callee_function.returning is True:
                    fakeret_edge = FunctionFakeRetEdge(cfg_node, return_site, current_function_addr, confirmed=True)
                    func_edges.append(fakeret_edge)
                    ret_edge = FunctionReturnEdge(new_function_addr, return_site, current_function_addr)
                    func_edges.append(ret_edge)

                    # Also, keep tracing from the return site
                    ce = CFGJob(return_site, current_function_addr, 'Ijk_FakeRet', last_addr=addr, src_node=cfg_node,
                                src_stmt_idx=stmt_idx, src_ins_addr=ins_addr, returning_source=new_function_addr,
                                syscall=is_syscall, func_edges=func_edges)
                    self._pending_jobs.add_job(ce)
                    # register this job to this function
                    self._register_analysis_job(current_function_addr, ce)
                elif callee_function is not None and callee_function.returning is False:
                    pass # Don't go past a call that does not return!
                else:
                    # HACK: We don't know where we are jumping.  Let's assume we fakeret to the
                    # next instruction after the block
                    # TODO: FIXME: There are arch-specific hints to give the correct ret site
                    # Such as looking for constant values of LR in this block for ARM stuff.
                    fakeret_edge = FunctionFakeRetEdge(cfg_node, return_site, current_function_addr, confirmed=None)
                    func_edges.append(fakeret_edge)
                    fr = FunctionReturn(new_function_addr, current_function_addr, addr, return_site)
                    if fr not in self._function_returns[new_function_addr]:
                        self._function_returns[new_function_addr].add(fr)
                    ce = CFGJob(return_site, current_function_addr, 'Ijk_FakeRet', last_addr=addr, src_node=cfg_node,
                                src_stmt_idx=stmt_idx, src_ins_addr=ins_addr, returning_source=new_function_addr,
                                syscall=is_syscall, func_edges=func_edges)
                    self._pending_jobs.add_job(ce)
                    # register this job to this function
                    self._register_analysis_job(current_function_addr, ce)


        return jobs