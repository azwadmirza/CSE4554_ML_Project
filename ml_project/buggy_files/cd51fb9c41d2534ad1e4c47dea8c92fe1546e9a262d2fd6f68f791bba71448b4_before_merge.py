    def _replace_parallel_functions(self, blocks):
        """
        Replace functions with their parallel implemntation in
        replace_functions_map if available.
        The implementation code is inlined to enable more optimization.
        """
        from numba.inline_closurecall import inline_closure_call
        work_list = list(blocks.items())
        while work_list:
            label, block = work_list.pop()
            for i, instr in enumerate(block.body):
                if isinstance(instr, ir.Assign):
                    lhs = instr.target
                    lhs_typ = self.typemap[lhs.name]
                    expr = instr.value
                    if isinstance(expr, ir.Expr) and expr.op == 'call':
                        # Try inline known calls with their parallel implementations
                        def replace_func():
                            func_def = get_definition(self.func_ir, expr.func)
                            callname = find_callname(self.func_ir, expr)
                            repl_func = replace_functions_map.get(callname, None)
                            require(repl_func != None)
                            typs = tuple(self.typemap[x.name] for x in expr.args)
                            try:
                                new_func =  repl_func(lhs_typ, *typs)
                            except:
                                new_func = None
                            require(new_func != None)
                            g = copy.copy(self.func_ir.func_id.func.__globals__)
                            g['numba'] = numba
                            g['np'] = numpy
                            g['math'] = math
                            # inline the parallel implementation
                            inline_closure_call(self.func_ir, g,
                                            block, i, new_func, self.typingctx, typs,
                                            self.typemap, self.calltypes, work_list)
                            return True
                        if guard(replace_func):
                            break
                    elif (isinstance(expr, ir.Expr) and expr.op == 'getattr' and
                          expr.attr == 'dtype'):
                        # Replace getattr call "A.dtype" with the actual type itself.
                        # This helps remove superfulous dependencies from parfor.
                        typ = self.typemap[expr.value.name]
                        if isinstance(typ, types.npytypes.Array):
                            dtype = typ.dtype
                            scope = block.scope
                            loc = instr.loc
                            g_np_var = ir.Var(scope, mk_unique_var("$np_g_var"), loc)
                            self.typemap[g_np_var.name] = types.misc.Module(numpy)
                            g_np = ir.Global('np', numpy, loc)
                            g_np_assign = ir.Assign(g_np, g_np_var, loc)
                            typ_var = ir.Var(scope, mk_unique_var("$np_typ_var"), loc)
                            self.typemap[typ_var.name] = types.DType(dtype)
                            dtype_str = str(dtype)
                            if dtype_str == 'bool':
                                dtype_str = 'bool_'
                            np_typ_getattr = ir.Expr.getattr(g_np_var, dtype_str, loc)
                            typ_var_assign = ir.Assign(np_typ_getattr, typ_var, loc)
                            instr.value = typ_var
                            block.body.insert(0, typ_var_assign)
                            block.body.insert(0, g_np_assign)
                            break