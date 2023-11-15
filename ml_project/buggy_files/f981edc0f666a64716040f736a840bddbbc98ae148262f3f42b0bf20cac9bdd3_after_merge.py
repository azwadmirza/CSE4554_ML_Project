    def run_pass(self, state):
        from numba import njit
        func_ir = state.func_ir
        mutated = False
        for idx, blk in func_ir.blocks.items():
            for stmt in blk.body:
                if isinstance(stmt, ir.Assign):
                    if isinstance(stmt.value, ir.Expr):
                        if stmt.value.op == "make_function":
                            node = stmt.value
                            getdef = func_ir.get_definition
                            kw_default = getdef(node.defaults)
                            ok = False
                            if (kw_default is None or
                                    isinstance(kw_default, ir.Const)):
                                ok = True
                            elif isinstance(kw_default, tuple):
                                ok = all([isinstance(getdef(x), ir.Const)
                                          for x in kw_default])
                            elif isinstance(kw_default, ir.Expr):
                                if kw_default.op != "build_tuple":
                                    continue
                                ok = all([isinstance(getdef(x), ir.Const)
                                          for x in kw_default.items])
                            if not ok:
                                print("NOT OK")
                                continue

                            pyfunc = convert_code_obj_to_function(node, func_ir)
                            func = njit()(pyfunc)
                            new_node = ir.Global(node.code.co_name, func,
                                                 stmt.loc)
                            stmt.value = new_node
                            mutated |= True

        # if a change was made the del ordering is probably wrong, patch up
        if mutated:
            post_proc = postproc.PostProcessor(func_ir)
            post_proc.run()

        return mutated