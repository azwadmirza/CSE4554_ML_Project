    def run_pass(self, state):
        """Run inlining of overloads
        """
        if config.DEBUG or self._DEBUG:
            print('before overload inline'.center(80, '-'))
            print(state.func_ir.dump())
            print(''.center(80, '-'))
        modified = False
        work_list = list(state.func_ir.blocks.items())
        # use a work list, look for call sites via `ir.Expr.op == call` and
        # then pass these to `self._do_work` to make decisions about inlining.
        while work_list:
            label, block = work_list.pop()
            for i, instr in enumerate(block.body):
                if isinstance(instr, ir.Assign):
                    expr = instr.value
                    if isinstance(expr, ir.Expr) and expr.op == 'call':
                        if guard(self._do_work, state, work_list, block, i,
                                 expr):
                            modified = True
                            break  # because block structure changed

        if config.DEBUG or self._DEBUG:
            print('after overload inline'.center(80, '-'))
            print(state.func_ir.dump())
            print(''.center(80, '-'))

        if modified:
            # clean up blocks
            dead_code_elimination(state.func_ir,
                                  typemap=state.type_annotation.typemap)
            # clean up unconditional branches that appear due to inlined
            # functions introducing blocks
            state.func_ir.blocks = simplify_CFG(state.func_ir.blocks)

        if config.DEBUG or self._DEBUG:
            print('after overload inline DCE'.center(80, '-'))
            print(state.func_ir.dump())
            print(''.center(80, '-'))

        return True