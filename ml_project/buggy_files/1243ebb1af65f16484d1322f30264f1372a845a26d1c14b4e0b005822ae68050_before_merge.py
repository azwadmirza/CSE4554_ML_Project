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