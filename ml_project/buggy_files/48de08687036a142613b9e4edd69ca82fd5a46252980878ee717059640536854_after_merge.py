    def run(self):
        """ Finds all calls to StencilFuncs in the IR and converts them to parfor.
        """
        from numba.stencil import StencilFunc

        # Get all the calls in the function IR.
        call_table, _ = get_call_table(self.func_ir.blocks)
        stencil_calls = []
        stencil_dict = {}
        for call_varname, call_list in call_table.items():
            for one_call in call_list:
                if isinstance(one_call, StencilFunc):
                    # Remember all calls to StencilFuncs.
                    stencil_calls.append(call_varname)
                    stencil_dict[call_varname] = one_call
        if not stencil_calls:
            return  # return early if no stencil calls found

        # find and transform stencil calls
        for label, block in self.func_ir.blocks.items():
            for i, stmt in reversed(list(enumerate(block.body))):
                # Found a call to a StencilFunc.
                if (isinstance(stmt, ir.Assign)
                        and isinstance(stmt.value, ir.Expr)
                        and stmt.value.op == 'call'
                        and stmt.value.func.name in stencil_calls):
                    kws = dict(stmt.value.kws)
                    # Create dictionary of input argument number to
                    # the argument itself.
                    input_dict = {i: stmt.value.args[i] for i in
                                                    range(len(stmt.value.args))}
                    in_args = stmt.value.args
                    arg_typemap = tuple(self.typemap[i.name] for i in in_args)
                    for arg_type in arg_typemap:
                        if isinstance(arg_type, types.BaseTuple):
                            raise ValueError("Tuple parameters not supported " \
                                "for stencil kernels in parallel=True mode.")

                    out_arr = kws.get('out')

                    # Get the StencilFunc object corresponding to this call.
                    sf = stencil_dict[stmt.value.func.name]
                    stencil_ir, rt, arg_to_arr_dict = get_stencil_ir(sf,
                            self.typingctx, arg_typemap,
                            block.scope, block.loc, input_dict,
                            self.typemap, self.calltypes)
                    index_offsets = sf.options.get('index_offsets', None)
                    gen_nodes = self._mk_stencil_parfor(label, in_args, out_arr,
                            stencil_ir, index_offsets, stmt.target, rt, sf,
                            arg_to_arr_dict)
                    block.body = block.body[:i] + gen_nodes + block.body[i+1:]
                # Found a call to a stencil via numba.stencil().
                elif (isinstance(stmt, ir.Assign)
                        and isinstance(stmt.value, ir.Expr)
                        and stmt.value.op == 'call'
                        and guard(find_callname, self.func_ir, stmt.value)
                                    == ('stencil', 'numba')):
                    # remove dummy stencil() call
                    stmt.value = ir.Const(0, stmt.loc)