    def run(self):
        """Run inline closure call pass.
        """
        modified = False
        work_list = list(self.func_ir.blocks.items())
        debug_print = _make_debug_print("InlineClosureCallPass")
        debug_print("START")
        while work_list:
            label, block = work_list.pop()
            for i in range(len(block.body)):
                instr = block.body[i]
                if isinstance(instr, ir.Assign):
                    lhs = instr.target
                    expr = instr.value
                    if isinstance(expr, ir.Expr) and expr.op == 'call':
                        func_def = guard(_get_definition, self.func_ir, expr.func)
                        debug_print("found call to ", expr.func, " def = ", func_def)
                        if isinstance(func_def, ir.Expr) and func_def.op == "make_function":
                            new_blocks = self.inline_closure_call(block, i, func_def)
                            for block in new_blocks:
                                work_list.append(block)
                            modified = True
                            # current block is modified, skip the rest
                            break

        if enable_inline_arraycall:
            # Identify loop structure
            if modified:
                # Need to do some cleanups if closure inlining kicked in
                merge_adjacent_blocks(self.func_ir)
            cfg = compute_cfg_from_blocks(self.func_ir.blocks)
            debug_print("start inline arraycall")
            _debug_dump(cfg)
            loops = cfg.loops()
            sized_loops = [(k, len(loops[k].body)) for k in loops.keys()]
            visited = []
            # We go over all loops, bigger loops first (outer first)
            for k, s in sorted(sized_loops, key=lambda tup: tup[1], reverse=True):
                visited.append(k)
                if guard(_inline_arraycall, self.func_ir, cfg, visited, loops[k],
                        self.flags.auto_parallel):
                    modified = True
            if modified:
                _fix_nested_array(self.func_ir)

        if modified:
            remove_dels(self.func_ir.blocks)
            # repeat dead code elimintation until nothing can be further
            # removed
            while (remove_dead(self.func_ir.blocks, self.func_ir.arg_names)):
                pass
            self.func_ir.blocks = rename_labels(self.func_ir.blocks)
        debug_print("END")