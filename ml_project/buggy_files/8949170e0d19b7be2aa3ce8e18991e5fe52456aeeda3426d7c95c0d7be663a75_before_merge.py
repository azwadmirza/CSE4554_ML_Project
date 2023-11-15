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
            succ = self.project.factory.successors(tmp_state).flat_successors[0]
            try:
                syscall_stub = self.project.simos.syscall(succ)
                if syscall_stub:  # can be None if simos is not a subclass of SimUserspac
                    syscall_addr = syscall_stub.addr
                    target_addr = syscall_addr
                else:
                    target_addr = self._unresolvable_target_addr
            except AngrUnsupportedSyscallError:
                target_addr = self._unresolvable_target_addr

        new_function_addr = target_addr
        if irsb is None:
            return_site = None
        else:
            return_site = addr + irsb.size  # We assume the program will always return to the succeeding position

        if new_function_addr is not None:
            r = self._function_add_call_edge(new_function_addr, cfg_node, return_site, current_function_addr,
                                             syscall=is_syscall, stmt_idx=stmt_idx, ins_addr=ins_addr)
            if not r:
                return [ ]

        if new_function_addr is not None:
            # Keep tracing from the call
            ce = CFGJob(target_addr, new_function_addr, jumpkind, last_addr=addr, src_node=cfg_node,
                        src_stmt_idx=stmt_idx, src_ins_addr=ins_addr, syscall=is_syscall)
            jobs.append(ce)

        if return_site is not None:
            # Also, keep tracing from the return site
            ce = CFGJob(return_site, current_function_addr, 'Ijk_FakeRet', last_addr=addr, src_node=cfg_node,
                        src_stmt_idx=stmt_idx, src_ins_addr=ins_addr, returning_source=new_function_addr,
                        syscall=is_syscall)
            self._pending_jobs.add_job(ce)
            # register this job to this function
            self._register_analysis_job(current_function_addr, ce)

        if new_function_addr is not None:
            callee_function = self.kb.functions.function(addr=new_function_addr, syscall=is_syscall)

            if callee_function.returning is True:
                if return_site is not None:
                    self._function_add_fakeret_edge(return_site, cfg_node, current_function_addr,
                                                    confirmed=True)
                    self._function_add_return_edge(new_function_addr, return_site, current_function_addr)
            elif callee_function.returning is False:
                # The function does not return - there is no fake ret edge
                pass
            else:
                if return_site is not None:
                    self._function_add_fakeret_edge(return_site, cfg_node, current_function_addr,
                                                    confirmed=None)
                    fr = FunctionReturn(new_function_addr, current_function_addr, addr, return_site)
                    if fr not in self._function_returns[new_function_addr]:
                        self._function_returns[new_function_addr].append(fr)

        return jobs