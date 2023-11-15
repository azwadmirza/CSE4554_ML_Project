    def run_pass(self, state):
        """Run inlining of overloads
        """
        if self._DEBUG:
            print('before overload inline'.center(80, '-'))
            print(state.func_id.unique_name)
            print(state.func_ir.dump())
            print(''.center(80, '-'))
        from numba.core.inline_closurecall import (InlineWorker,
                                                   callee_ir_validator)
        inline_worker = InlineWorker(state.typingctx,
                                     state.targetctx,
                                     state.locals,
                                     state.pipeline,
                                     state.flags,
                                     callee_ir_validator,
                                     state.typemap,
                                     state.calltypes,
                                     )
        modified = False
        work_list = list(state.func_ir.blocks.items())
        # use a work list, look for call sites via `ir.Expr.op == call` and
        # then pass these to `self._do_work` to make decisions about inlining.
        while work_list:
            label, block = work_list.pop()
            for i, instr in enumerate(block.body):
                if isinstance(instr, ir.Assign):
                    expr = instr.value
                    if isinstance(expr, ir.Expr):
                        if expr.op == 'call':
                            workfn = self._do_work_call
                        elif expr.op == 'getattr':
                            workfn = self._do_work_getattr
                        else:
                            continue

                        if guard(workfn, state, work_list, block, i, expr,
                                 inline_worker):
                            modified = True
                            break  # because block structure changed

        if self._DEBUG:
            print('after overload inline'.center(80, '-'))
            print(state.func_id.unique_name)
            print(state.func_ir.dump())
            print(''.center(80, '-'))

        if modified:
            # Remove dead blocks, this is safe as it relies on the CFG only.
            cfg = compute_cfg_from_blocks(state.func_ir.blocks)
            for dead in cfg.dead_nodes():
                del state.func_ir.blocks[dead]
            # clean up blocks
            dead_code_elimination(state.func_ir,
                                  typemap=state.type_annotation.typemap)
            # clean up unconditional branches that appear due to inlined
            # functions introducing blocks
            state.func_ir.blocks = simplify_CFG(state.func_ir.blocks)

        if self._DEBUG:
            print('after overload inline DCE'.center(80, '-'))
            print(state.func_id.unique_name)
            print(state.func_ir.dump())
            print(''.center(80, '-'))
        return True