    def run(self):
        for inst in self._iter_inst():
            fname = "op_%s" % inst.opname
            fn = getattr(self, fname, None)
            if fn is not None:
                fn(inst)
            elif inst.is_jump:
                # this catches e.g. try... except
                l = Loc(self.bytecode.func_id.filename, inst.lineno)
                if inst.opname in {"SETUP_EXCEPT", "SETUP_FINALLY"}:
                    msg = "'try' block not supported until python3.7 or later"
                else:
                    msg = "Use of unsupported opcode (%s) found" % inst.opname
                raise UnsupportedError(msg, loc=l)
            else:
                # Non-jump instructions are ignored
                pass  # intentionally

        # Close all blocks
        for cur, nxt in zip(self.blockseq, self.blockseq[1:]):
            blk = self.blocks[cur]
            if not blk.outgoing_jumps and not blk.terminating:
                blk.outgoing_jumps[nxt] = 0

        graph = CFGraph()
        for b in self.blocks:
            graph.add_node(b)
        for b in self.blocks.values():
            for out, pops in b.outgoing_jumps.items():
                graph.add_edge(b.offset, out, pops)
        graph.set_entry_point(min(self.blocks))
        graph.process()
        self.graph = graph

        # Fill incoming
        for b in utils.itervalues(self.blocks):
            for out, pops in b.outgoing_jumps.items():
                self.blocks[out].incoming_jumps[b.offset] = pops

        # Find liveblocks
        self.liveblocks = dict((i, self.blocks[i])
                               for i in self.graph.nodes())

        for lastblk in reversed(self.blockseq):
            if lastblk in self.liveblocks:
                break
        else:
            raise AssertionError("No live block that exits!?")

        # Find backbone
        backbone = self.graph.backbone()
        # Filter out in loop blocks (Assuming no other cyclic control blocks)
        # This is to unavoid variable defined in loops to be considered as
        # function scope.
        inloopblocks = set()

        for b in self.blocks.keys():
            if self.graph.in_loops(b):
                inloopblocks.add(b)

        self.backbone = backbone - inloopblocks