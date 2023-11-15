    def unroll_loop(self, state, loop_info):
        # The general idea here is to:
        # 1. Find *a* getitem that conforms to the literal_unroll semantic,
        #    i.e. one that is targeting a tuple with a loop induced index
        # 2. Compute a structure from the tuple that describes which
        #    iterations of a loop will have which type
        # 3. Generate a switch table in IR form for the structure in 2
        # 4. Switch out getitems for the tuple for a `typed_getitem`
        # 5. Inject switch table as replacement loop body
        # 6. Patch up
        func_ir = state.func_ir
        getitem_target = loop_info.arg
        target_ty = state.typemap[getitem_target.name]
        assert isinstance(target_ty, self._accepted_types)

        # 1. find a "getitem" that conforms
        tuple_getitem = []
        for lbl in loop_info.loop.body:
            blk = func_ir.blocks[lbl]
            for stmt in blk.body:
                if isinstance(stmt, ir.Assign):
                    if isinstance(stmt.value,
                                  ir.Expr) and stmt.value.op == "getitem":
                        # try a couple of spellings... a[i] and ref(a)[i]
                        if stmt.value.value != getitem_target:
                            dfn = func_ir.get_definition(stmt.value.value)
                            args = getattr(dfn, 'args', False)
                            if not args:
                                continue
                            if not args[0] == getitem_target:
                                continue
                        target_ty = state.typemap[getitem_target.name]
                        if not isinstance(target_ty, self._accepted_types):
                            continue
                        tuple_getitem.append(stmt)

        if not tuple_getitem:
            msg = ("Loop unrolling analysis has failed, there's no getitem "
                   "in loop body that conforms to literal_unroll "
                   "requirements.")
            LOC = func_ir.blocks[loop_info.loop.header].loc
            raise errors.CompilerError(msg, LOC)

        # 2. get switch data
        switch_data = self.analyse_tuple(target_ty)

        # 3. generate switch IR
        index = func_ir._definitions[tuple_getitem[0].value.index.name][0]
        branches = self.gen_switch(switch_data, index)

        # 4. swap getitems for a typed_getitem, these are actually just
        # placeholders at this point. When the loop is duplicated they can
        # be swapped for a typed_getitem of the correct type or if the item
        # is literal it can be shoved straight into the duplicated loop body
        for item in tuple_getitem:
            old = item.value
            new = ir.Expr.typed_getitem(
                old.value, types.void, old.index, old.loc)
            item.value = new

        # 5. Inject switch table

        # Find the actual loop without the header (that won't get replaced)
        # and derive some new IR for this set of blocks
        this_loop = loop_info.loop
        this_loop_body = this_loop.body - \
            set([this_loop.header])
        loop_blocks = {
            x: func_ir.blocks[x] for x in this_loop_body}
        new_ir = func_ir.derive(loop_blocks)

        # Work out what is live on entry and exit so as to prevent
        # replacement (defined vars can escape, used vars live at the header
        # need to remain as-is so their references are correct, they can
        # also escape).

        usedefs = compute_use_defs(func_ir.blocks)
        idx = this_loop.header
        keep = set()
        keep |= usedefs.usemap[idx] | usedefs.defmap[idx]
        keep |= func_ir.variable_lifetime.livemap[idx]
        dont_replace = [x for x in (keep)]

        # compute the unrolled body
        unrolled_body = self.inject_loop_body(
            branches, new_ir, max(func_ir.blocks.keys()) + 1,
            dont_replace, switch_data)

        # 6. Patch in the unrolled body and fix up
        blks = state.func_ir.blocks
        orig_lbl = tuple(this_loop_body)

        replace, *delete = orig_lbl
        unroll, header_block = unrolled_body, this_loop.header
        unroll_lbl = [x for x in sorted(unroll.blocks.keys())]
        blks[replace] = unroll.blocks[unroll_lbl[0]]
        [blks.pop(d) for d in delete]
        for k in unroll_lbl[1:]:
            blks[k] = unroll.blocks[k]
        # stitch up the loop predicate true -> new loop body jump
        blks[header_block].body[-1].truebr = replace