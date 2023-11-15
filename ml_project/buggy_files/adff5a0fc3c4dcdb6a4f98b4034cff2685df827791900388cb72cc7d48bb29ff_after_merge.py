    def apply_transform(self, state):
        # compute new CFG
        func_ir = state.func_ir
        cfg = compute_cfg_from_blocks(func_ir.blocks)
        # find loops
        loops = cfg.loops()

        # 0. Find the loops containing literal_unroll and store this
        #    information
        literal_unroll_info = dict()
        unroll_info = namedtuple(
            "unroll_info", [
                "loop", "call", "arg", "getitem"])

        def get_call_args(init_arg, want):
            # Chases the assignment of a called value back through a specific
            # call to a global function "want" and returns the arguments
            # supplied to that function's call
            some_call = get_definition(func_ir, init_arg)
            if not isinstance(some_call, ir.Expr):
                raise GuardException
            if not some_call.op == "call":
                raise GuardException
            the_global = get_definition(func_ir, some_call.func)
            if not isinstance(the_global, ir.Global):
                raise GuardException
            if the_global.value is not want:
                raise GuardException
            return some_call

        for lbl, loop in loops.items():
            # TODO: check the loop head has literal_unroll, if it does but
            # does not conform to the following then raise

            # scan loop header
            iternexts = [_ for _ in
                         func_ir.blocks[loop.header].find_exprs('iternext')]
            if len(iternexts) != 1:
                return False
            for iternext in iternexts:
                # Walk the canonicalised loop structure and check it
                # Check loop form range(literal_unroll(container)))
                phi = guard(get_definition, func_ir,  iternext.value)
                if phi is None:
                    continue

                # check call global "range"
                range_call = guard(get_call_args, phi.value, range)
                if range_call is None:
                    continue
                range_arg = range_call.args[0]

                # check call global "len"
                len_call = guard(get_call_args, range_arg, len)
                if len_call is None:
                    continue
                len_arg = len_call.args[0]

                # check literal_unroll
                literal_unroll_call = guard(get_definition, func_ir, len_arg)
                if literal_unroll_call is None:
                    continue
                if not isinstance(literal_unroll_call, ir.Expr):
                    continue
                if literal_unroll_call.op != "call":
                    continue
                literal_func = getattr(literal_unroll_call, 'func', None)
                if not literal_func:
                    continue
                call_func = guard(get_definition, func_ir,
                                  literal_unroll_call.func)
                if call_func is None:
                    continue
                call_func = call_func.value

                if call_func is literal_unroll:
                    assert len(literal_unroll_call.args) == 1
                    arg = literal_unroll_call.args[0]
                    typemap = state.typemap
                    resolved_arg = guard(get_definition, func_ir, arg,
                                         lhs_only=True)
                    ty = typemap[resolved_arg.name]
                    assert isinstance(ty, self._accepted_types)
                    # loop header is spelled ok, now make sure the body
                    # actually contains a getitem

                    # find a "getitem"
                    tuple_getitem = None
                    for lbl in loop.body:
                        blk = func_ir.blocks[lbl]
                        for stmt in blk.body:
                            if isinstance(stmt, ir.Assign):
                                if (isinstance(stmt.value, ir.Expr) and
                                        stmt.value.op == "getitem"):
                                    # check for something like a[i]
                                    if stmt.value.value != arg:
                                        # that failed, so check for the
                                        # definition
                                        dfn = guard(get_definition, func_ir,
                                                    stmt.value.value)
                                        if dfn is None:
                                            continue
                                        try:
                                            args = getattr(dfn, 'args', False)
                                        except KeyError:
                                            continue
                                        if not args:
                                            continue
                                        if not args[0] == arg:
                                            continue
                                    target_ty = state.typemap[arg.name]
                                    if not isinstance(target_ty,
                                                      self._accepted_types):
                                        continue
                                    tuple_getitem = stmt
                                    break
                        if tuple_getitem:
                            break
                    else:
                        continue  # no getitem in this loop

                    ui = unroll_info(loop, literal_unroll_call, arg,
                                     tuple_getitem)
                    literal_unroll_info[lbl] = ui

        if not literal_unroll_info:
            return False

        # 1. Validate loops, must not have any calls to literal_unroll
        for test_lbl, test_loop in literal_unroll_info.items():
            for ref_lbl, ref_loop in literal_unroll_info.items():
                if test_lbl == ref_lbl:  # comparing to self! skip
                    continue
                if test_loop.loop.header in ref_loop.loop.body:
                    msg = ("Nesting of literal_unroll is unsupported")
                    loc = func_ir.blocks[test_loop.loop.header].loc
                    raise errors.UnsupportedError(msg, loc)

        # 2. Do the unroll, get a loop and process it!
        lbl, info = literal_unroll_info.popitem()
        self.unroll_loop(state, info)

        # 3. Rebuild the state, the IR has taken a hammering
        func_ir.blocks = simplify_CFG(func_ir.blocks)
        post_proc = postproc.PostProcessor(func_ir)
        post_proc.run()
        if self._DEBUG:
            print('-' * 80 + "END OF PASS, SIMPLIFY DONE")
            func_ir.dump()
        func_ir._definitions = build_definitions(func_ir.blocks)
        return True