    def _remove_redundant_overlapping_blocks(self):
        """
        On some architectures there are sometimes garbage bytes (usually nops) between functions in order to properly
        align the succeeding function. CFGFast does a linear sweeping which might create duplicated blocks for
        function epilogues where one block starts before the garbage bytes and the other starts after the garbage bytes.

        This method enumerates all blocks and remove overlapping blocks if one of them is aligned to 0x10 and the other
        contains only garbage bytes.

        :return: None
        """

        sorted_nodes = sorted(self.graph.nodes(), key=lambda n: n.addr if n is not None else 0)

        all_plt_stub_addrs = set(itertools.chain.from_iterable(obj.reverse_plt.keys() for obj in self.project.loader.all_objects if isinstance(obj, cle.MetaELF)))

        # go over the list. for each node that is the beginning of a function and is not properly aligned, if its
        # leading instruction is a single-byte or multi-byte nop, make sure there is another CFGNode starts after the
        # nop instruction

        nodes_to_append = {}
        # pylint:disable=too-many-nested-blocks
        for a in sorted_nodes:
            if a.addr in self.functions and a.addr not in all_plt_stub_addrs and \
                    not self._addr_hooked_or_syscall(a.addr):
                all_in_edges = self.graph.in_edges(a, data=True)
                if not any([data['jumpkind'] == 'Ijk_Call' for _, _, data in all_in_edges]):
                    # no one is calling it
                    # this function might be created from linear sweeping
                    try:
                        block = self._lift(a.addr, size=0x10 - (a.addr % 0x10), opt_level=1)
                        vex_block = block.vex
                    except SimTranslationError:
                        continue

                    nop_length = None

                    if self._is_noop_block(vex_block):
                        # fast path: in most cases, the entire block is a single byte or multi-byte nop, which VEX
                        # optimizer is able to tell
                        nop_length = block.size

                    else:
                        # this is not a no-op block. Determine where nop instructions terminate.
                        insns = block.capstone.insns
                        if insns:
                            nop_length = self._get_nop_length(insns)

                    if nop_length <= 0:
                        continue

                    # leading nop for alignment.
                    next_node_addr = a.addr + nop_length
                    if nop_length < a.size and \
                            not (next_node_addr in self._nodes or next_node_addr in nodes_to_append):
                        # create a new CFGNode that starts there
                        next_node_size = a.size - nop_length
                        next_node = CFGNode(next_node_addr, next_node_size, self,
                                            function_address=next_node_addr,
                                            instruction_addrs=tuple(i for i in a.instruction_addrs
                                                                      if next_node_addr <= i
                                                                      < next_node_addr + next_node_size
                                                                    ),
                                            thumb=a.thumb,
                                            byte_string=None if a.byte_string is None else a.byte_string[nop_length:],
                                            )
                        # create edges accordingly
                        all_out_edges = self.graph.out_edges(a, data=True)
                        for _, dst, data in all_out_edges:
                            self.graph.add_edge(next_node, dst, **data)

                        nodes_to_append[next_node_addr] = next_node

                        # make sure there is a function begins there
                        try:
                            snippet = self._to_snippet(addr=next_node_addr, size=next_node_size,
                                                       base_state=self._base_state)
                            self.functions._add_node(next_node_addr, snippet)
                        except (SimEngineError, SimMemoryError):
                            continue

        # append all new nodes to sorted nodes
        if nodes_to_append:
            sorted_nodes = sorted(sorted_nodes + nodes_to_append.values(), key=lambda n: n.addr if n is not None else 0)

        removed_nodes = set()

        a = None  # it always hold the very recent non-removed node

        for i in xrange(len(sorted_nodes)):

            if a is None:
                a = sorted_nodes[0]
                continue

            b = sorted_nodes[i]
            if self._addr_hooked_or_syscall(b.addr):
                continue

            if b in removed_nodes:
                # skip all removed nodes
                continue

            if a.addr <= b.addr and \
                    (a.addr + a.size > b.addr):
                # They are overlapping

                try:
                    block = self.project.factory.fresh_block(a.addr, b.addr - a.addr, backup_state=self._base_state)
                except SimTranslationError:
                    a = b
                    continue
                if block.capstone.insns and all([ self._is_noop_insn(insn) for insn in block.capstone.insns ]):
                    # It's a big nop - no function starts with nop

                    # add b to indices
                    self._nodes[b.addr] = b
                    self._nodes_by_addr[b.addr].append(b)

                    # shrink a
                    self._shrink_node(a, b.addr - a.addr, remove_function=False)

                    a = b
                    continue

                all_functions = self.kb.functions

                # now things are a little harder
                # if there is no incoming edge to b, we should replace b with a
                # this is mostly because we misidentified the function beginning. In fact a is the function beginning,
                # but somehow we thought b is the beginning
                if a.addr + a.size == b.addr + b.size:
                    in_edges = len([ _ for _, _, data in self.graph.in_edges([b], data=True) ])
                    if in_edges == 0:
                        # we use node a to replace node b
                        # link all successors of b to a
                        for _, dst, data in self.graph.out_edges([b], data=True):
                            self.graph.add_edge(a, dst, **data)

                        if b.addr in self._nodes:
                            del self._nodes[b.addr]
                        if b.addr in self._nodes_by_addr and b in self._nodes_by_addr[b.addr]:
                            self._nodes_by_addr[b.addr].remove(b)

                        self.graph.remove_node(b)

                        if b.addr in all_functions:
                            del all_functions[b.addr]

                        # skip b
                        removed_nodes.add(b)

                        continue

                # next case - if b is directly from function prologue detection, or a basic block that is a successor of
                # a wrongly identified basic block, we might be totally misdecoding b
                if b.instruction_addrs[0] not in a.instruction_addrs:
                    # use a, truncate b

                    new_b_addr = a.addr + a.size  # b starts right after a terminates
                    new_b_size = b.addr + b.size - new_b_addr  # this may not be the size we want, since b might be
                                                               # misdecoded

                    # totally remove b
                    if b.addr in self._nodes:
                        del self._nodes[b.addr]
                    if b.addr in self._nodes_by_addr and b in self._nodes_by_addr[b.addr]:
                        self._nodes_by_addr[b.addr].remove(b)

                    self.graph.remove_node(b)

                    if b.addr in all_functions:
                        del all_functions[b.addr]

                    removed_nodes.add(b)

                    if new_b_size > 0:
                        # there are still some parts left in node b - we don't want to lose it
                        self._scan_block(new_b_addr, a.function_address, None, None, None, None)

                    continue

                # for other cases, we'll let them be for now

            a = b # update a