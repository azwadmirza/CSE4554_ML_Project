    def _process_irrational_function_starts(self, functions, predetermined_function_addrs, blockaddr_to_function):
        """
        Functions that are identified via function prologues can be starting after the actual beginning of the function.
        For example, the following function (with an incorrect start) might exist after a CFG recovery:

        sub_8049f70:
          push    esi

        sub_8049f71:
          sub     esp, 0A8h
          mov     esi, [esp+0ACh+arg_0]
          mov     [esp+0ACh+var_88], 0

        If the following conditions are met, we will remove the second function and merge it into the first function:
        - The second function is not called by other code.
        - The first function has only one jumpout site, which points to the second function.
        - The first function and the second function are adjacent.

        :param FunctionManager functions:   All functions that angr recovers.
        :return:                            A set of addresses of all removed functions.
        :rtype:                             set
        """

        addrs = sorted(k for k in functions.keys()
                       if not self.project.is_hooked(k) and not self.project.simos.is_syscall_addr(k))
        functions_to_remove = set()
        adjusted_cfgnodes = set()

        for addr_0, addr_1 in zip(addrs[:-1], addrs[1:]):

            if addr_1 in predetermined_function_addrs:
                continue

            func_0 = functions[addr_0]

            if len(func_0.block_addrs) == 1:
                block = next(func_0.blocks)
                if block.vex.jumpkind not in ('Ijk_Boring', 'Ijk_InvalICache'):
                    continue
                # Skip alignment blocks
                if self._is_noop_block(self.project.arch, block):
                    continue

                target = block.vex.next
                if type(target) is pyvex.IRExpr.Const:  # pylint: disable=unidiomatic-typecheck
                    target_addr = target.con.value
                elif type(target) in (pyvex.IRConst.U32, pyvex.IRConst.U64):  # pylint: disable=unidiomatic-typecheck
                    target_addr = target.value
                elif type(target) is int:  # pylint: disable=unidiomatic-typecheck
                    target_addr = target
                else:
                    continue

                if target_addr != addr_1:
                    continue

                cfgnode_0 = self.get_any_node(addr_0)
                cfgnode_1 = self.get_any_node(addr_1)

                # Are func_0 adjacent to func_1?
                if cfgnode_0.addr + cfgnode_0.size != addr_1:
                    continue

                # Merge block addr_0 and block addr_1
                l.debug("Merging function %#x into %#x.", addr_1, addr_0)
                self._merge_cfgnodes(cfgnode_0, cfgnode_1)
                adjusted_cfgnodes.add(cfgnode_0)
                adjusted_cfgnodes.add(cfgnode_1)

                # Merge it
                func_1 = functions[addr_1]
                for block_addr in func_1.block_addrs:
                    if block_addr == addr_1:
                        # Skip addr_1 (since it has been merged to the preceding block)
                        continue
                    merge_with = self._addr_to_function(addr_0, blockaddr_to_function, functions)
                    blockaddr_to_function[block_addr] = merge_with

                functions_to_remove.add(addr_1)

        for to_remove in functions_to_remove:
            del functions[to_remove]

        return functions_to_remove, adjusted_cfgnodes