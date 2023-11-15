    def run(self):
        """Run inline closure call pass.
        """
        # Analysis relies on ir.Del presence, strip out later
        pp = postproc.PostProcessor(self.func_ir)
        pp.run(True)

        modified = False
        work_list = list(self.func_ir.blocks.items())
        debug_print = _make_debug_print("InlineClosureCallPass")
        debug_print("START")
        while work_list:
            label, block = work_list.pop()
            for i, instr in enumerate(block.body):
                if isinstance(instr, ir.Assign):
                    lhs = instr.target
                    expr = instr.value
                    if isinstance(expr, ir.Expr) and expr.op == 'call':
                        call_name = guard(find_callname, self.func_ir, expr)
                        func_def = guard(get_definition, self.func_ir, expr.func)

                        if guard(self._inline_reduction,
                                 work_list, block, i, expr, call_name):
                            modified = True
                            break # because block structure changed

                        if guard(self._inline_closure,
                                work_list, block, i, func_def):
                            modified = True
                            break # because block structure changed

                        if guard(self._inline_stencil,
                                instr, call_name, func_def):
                            modified = True

        if enable_inline_arraycall:
            # Identify loop structure
            if modified:
                # Need to do some cleanups if closure inlining kicked in
                merge_adjacent_blocks(self.func_ir.blocks)
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
                         self.swapped, self.parallel_options.comprehension,
                         self.typed):
                    modified = True
            if modified:
                _fix_nested_array(self.func_ir)

        if modified:
            # run dead code elimination
            dead_code_elimination(self.func_ir)
            # do label renaming
            self.func_ir.blocks = rename_labels(self.func_ir.blocks)

        # inlining done, strip dels
        remove_dels(self.func_ir.blocks)

        debug_print("END")