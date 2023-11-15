    def subgraph(self, ins_addrs):
        """
        Generate a sub control flow graph of instruction addresses based on self.graph

        :param iterable ins_addrs: A collection of instruction addresses that should be included in the subgraph.
        :return networkx.DiGraph: A subgraph.
        """

        # find all basic blocks that include those instructions
        blocks = []
        block_addr_to_insns = {}

        for b in self._local_blocks.values():
            # TODO: should I call get_blocks?
            block = self._get_block(b.addr, size=b.size, byte_string=b.bytestr)
            common_insns = set(block.instruction_addrs).intersection(ins_addrs)
            if common_insns:
                blocks.append(b)
                block_addr_to_insns[b.addr] = sorted(common_insns)

       #subgraph = networkx.subgraph(self.graph, blocks)
        subgraph = self.graph.subgraph(blocks).copy()
        g = networkx.DiGraph()

        for n in subgraph.nodes():
            insns = block_addr_to_insns[n.addr]

            in_edges = subgraph.in_edges(n)
            # out_edges = subgraph.out_edges(n)
            if len(in_edges) > 1:
                # the first instruction address should be included
                if n.addr not in insns:
                    insns = [n.addr] + insns

            for src, _ in in_edges:
                last_instr = block_addr_to_insns[src.addr][-1]
                g.add_edge(last_instr, insns[0])

            for i in range(0, len(insns) - 1):
                g.add_edge(insns[i], insns[i + 1])

        return g