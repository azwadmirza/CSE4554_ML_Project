        def legalize_return_type(return_type, interp, targetctx):
            """
            Only accept array return type iff it is passed into the function.
            Reject function object return types if in nopython mode.
            """
            if (not targetctx.enable_nrt and
                    isinstance(return_type, types.Array)):
                # Walk IR to discover all arguments and all return statements
                retstmts = []
                caststmts = {}
                argvars = set()
                for bid, blk in interp.blocks.items():
                    for inst in blk.body:
                        if isinstance(inst, ir.Return):
                            retstmts.append(inst.value.name)
                        elif isinstance(inst, ir.Assign):
                            if (isinstance(inst.value, ir.Expr)
                                    and inst.value.op == 'cast'):
                                caststmts[inst.target.name] = inst.value
                            elif isinstance(inst.value, ir.Arg):
                                argvars.add(inst.target.name)

                assert retstmts, "No return statements?"

                for var in retstmts:
                    cast = caststmts.get(var)
                    if cast is None or cast.value.name not in argvars:
                        raise TypeError("Only accept returning of array passed "
                                        "into the function as argument")

            elif (isinstance(return_type, types.Function) or
                    isinstance(return_type, types.Phantom)):
                msg = "Can't return function object ({}) in nopython mode"
                raise TypeError(msg.format(return_type))