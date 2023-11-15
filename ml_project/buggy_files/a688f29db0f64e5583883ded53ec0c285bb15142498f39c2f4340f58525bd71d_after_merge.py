                        def replace_func():
                            func_def = get_definition(self.func_ir, expr.func)
                            callname = find_callname(self.func_ir, expr)
                            repl_func = replace_functions_map.get(callname, None)
                            if (repl_func is None and
                                len(callname) == 2 and
                                isinstance(callname[1], ir.Var) and
                                isinstance(self.typemap[callname[1].name],
                                           types.npytypes.Array)):
                                repl_func = replace_functions_ndarray.get(callname[0], None)
                                if repl_func is not None:
                                    # Add the array that the method is on to the arg list.
                                    expr.args.insert(0, callname[1])

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
                            # if the function being inlined has a function
                            # checking the inputs, find it and add it to globals
                            check = replace_functions_checkers_map.get(callname,
                                                                       None)
                            if check is not None:
                                g[check.name] = check.func
                            # inline the parallel implementation
                            new_blocks, _ = inline_closure_call(self.func_ir, g,
                                            block, i, new_func, self.typingctx, typs,
                                            self.typemap, self.calltypes, work_list)
                            call_table = get_call_table(new_blocks, topological_ordering=False)

                            # find the prange in the new blocks and record it for use in diagnostics
                            for call in call_table:
                                for k, v in call.items():
                                    if v[0] == 'internal_prange':
                                        swapped[k] = [callname, repl_func.__name__, func_def, block.body[i].loc]
                                        break
                            return True