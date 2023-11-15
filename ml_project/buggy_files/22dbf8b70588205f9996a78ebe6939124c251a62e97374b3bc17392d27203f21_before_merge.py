    def run(self, blocks=None, equiv_set=None):
        """run array shape analysis on the given IR blocks, resulting in
        modified IR and finalized EquivSet for each block.
        """
        if blocks == None:
            blocks = self.func_ir.blocks

        self.func_ir._definitions = build_definitions(self.func_ir.blocks)

        if equiv_set == None:
            init_equiv_set = SymbolicEquivSet(self.typemap)
        else:
            init_equiv_set = equiv_set

        dprint_func_ir(self.func_ir, "before array analysis", blocks)

        if config.DEBUG_ARRAY_OPT >= 1:
            print("ArrayAnalysis variable types: ", sorted(self.typemap.items()))
            print("ArrayAnalysis call types: ", self.calltypes)

        cfg = compute_cfg_from_blocks(blocks)
        topo_order = find_topo_order(blocks, cfg=cfg)
        # Traverse blocks in topological order
        for label in topo_order:
            block = blocks[label]
            scope = block.scope
            new_body = []
            equiv_set = None

            # equiv_set is the intersection of predecessors
            preds = cfg.predecessors(label)
            # some incoming edge may be pruned due to prior analysis
            if label in self.pruned_predecessors:
                pruned = self.pruned_predecessors[label]
            else:
                pruned = []
            # Go through each incoming edge, process prepended instructions and
            # calculate beginning equiv_set of current block as an intersection
            # of incoming ones.
            for (p, q) in preds:
                if p in pruned:
                    continue
                if p in self.equiv_sets:
                    from_set = self.equiv_sets[p].clone()
                    if (p, label) in self.prepends:
                        instrs = self.prepends[(p, label)]
                        for inst in instrs:
                            redefined = set()
                            self._analyze_inst(label, scope, from_set, inst, redefined)
                            # Remove anything multiply defined in this block 
                            # from every block equivs.
                            self.remove_redefineds(redefined)
                    if equiv_set == None:
                        equiv_set = from_set
                    else:
                        equiv_set = equiv_set.intersect(from_set)
                        redefined = set()
                        equiv_set.union_defs(from_set.defs, redefined)
                        # Remove anything multiply defined in this block 
                        # from every block equivs.
                        self.remove_redefineds(redefined)

            # Start with a new equiv_set if none is computed
            if equiv_set == None:
                equiv_set = init_equiv_set
            self.equiv_sets[label] = equiv_set
            # Go through instructions in a block, and insert pre/post
            # instructions as we analyze them.
            for inst in block.body:
                redefined = set()
                pre, post = self._analyze_inst(label, scope, equiv_set, inst, redefined)
                # Remove anything multiply defined in this block from every block equivs.
                self.remove_redefineds(redefined)
                for instr in pre:
                    new_body.append(instr)
                new_body.append(inst)
                for instr in post:
                    new_body.append(instr)
            block.body = new_body

        if config.DEBUG_ARRAY_OPT >= 1:
            self.dump()
            print("ArrayAnalysis post variable types: ", sorted(self.typemap.items()))
            print("ArrayAnalysis post call types: ", self.calltypes)

        dprint_func_ir(self.func_ir, "after array analysis", blocks)