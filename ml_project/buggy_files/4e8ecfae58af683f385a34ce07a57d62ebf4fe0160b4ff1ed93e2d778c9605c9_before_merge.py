    def _mk_stencil_parfor(self, label, in_args, out_arr, stencil_blocks,
                           index_offsets, target, return_type, stencil_func,
                           arg_to_arr_dict):
        """ Converts a set of stencil kernel blocks to a parfor.
        """
        gen_nodes = []

        if config.DEBUG_ARRAY_OPT == 1:
            print("_mk_stencil_parfor", label, in_args, out_arr, index_offsets,
                   return_type, stencil_func, stencil_blocks)
            ir_utils.dump_blocks(stencil_blocks)

        in_arr = in_args[0]
        # run copy propagate to replace in_args copies (e.g. a = A)
        in_arr_typ = self.typemap[in_arr.name]
        in_cps, out_cps = ir_utils.copy_propagate(stencil_blocks, self.typemap)
        name_var_table = ir_utils.get_name_var_table(stencil_blocks)

        ir_utils.apply_copy_propagate(
            stencil_blocks,
            in_cps,
            name_var_table,
            self.typemap,
            self.calltypes)
        if config.DEBUG_ARRAY_OPT == 1:
            print("stencil_blocks after copy_propagate")
            ir_utils.dump_blocks(stencil_blocks)
        ir_utils.remove_dead(stencil_blocks, self.func_ir.arg_names,
                             self.typemap)
        if config.DEBUG_ARRAY_OPT == 1:
            print("stencil_blocks after removing dead code")
            ir_utils.dump_blocks(stencil_blocks)

        # create parfor vars
        ndims = self.typemap[in_arr.name].ndim
        scope = in_arr.scope
        loc = in_arr.loc
        parfor_vars = []
        for i in range(ndims):
            parfor_var = ir.Var(scope, mk_unique_var(
                "$parfor_index_var"), loc)
            self.typemap[parfor_var.name] = types.intp
            parfor_vars.append(parfor_var)

        start_lengths, end_lengths = self._replace_stencil_accesses(
             stencil_blocks, parfor_vars, in_args, index_offsets, stencil_func,
             arg_to_arr_dict)

        if config.DEBUG_ARRAY_OPT == 1:
            print("stencil_blocks after replace stencil accesses")
            ir_utils.dump_blocks(stencil_blocks)

        # create parfor loop nests
        loopnests = []
        equiv_set = self.array_analysis.get_equiv_set(label)
        in_arr_dim_sizes = equiv_set.get_shape(in_arr)

        assert ndims == len(in_arr_dim_sizes)
        for i in range(ndims):
            last_ind = self._get_stencil_last_ind(in_arr_dim_sizes[i],
                                        end_lengths[i], gen_nodes, scope, loc)
            start_ind = self._get_stencil_start_ind(
                                        start_lengths[i], gen_nodes, scope, loc)
            # start from stencil size to avoid invalid array access
            loopnests.append(numba.parfor.LoopNest(parfor_vars[i],
                                start_ind, last_ind, 1))

        # We have to guarantee that the exit block has maximum label and that
        # there's only one exit block for the parfor body.
        # So, all return statements will change to jump to the parfor exit block.
        parfor_body_exit_label = max(stencil_blocks.keys()) + 1
        stencil_blocks[parfor_body_exit_label] = ir.Block(scope, loc)
        exit_value_var = ir.Var(scope, mk_unique_var("$parfor_exit_value"), loc)
        self.typemap[exit_value_var.name] = return_type.dtype

        # create parfor index var
        for_replacing_ret = []
        if ndims == 1:
            parfor_ind_var = parfor_vars[0]
        else:
            parfor_ind_var = ir.Var(scope, mk_unique_var(
                "$parfor_index_tuple_var"), loc)
            self.typemap[parfor_ind_var.name] = types.containers.UniTuple(
                types.intp, ndims)
            tuple_call = ir.Expr.build_tuple(parfor_vars, loc)
            tuple_assign = ir.Assign(tuple_call, parfor_ind_var, loc)
            for_replacing_ret.append(tuple_assign)

        if config.DEBUG_ARRAY_OPT == 1:
            print("stencil_blocks after creating parfor index var")
            ir_utils.dump_blocks(stencil_blocks)

        # empty init block
        init_block = ir.Block(scope, loc)
        if out_arr == None:
            in_arr_typ = self.typemap[in_arr.name]

            shape_name = ir_utils.mk_unique_var("in_arr_shape")
            shape_var = ir.Var(scope, shape_name, loc)
            shape_getattr = ir.Expr.getattr(in_arr, "shape", loc)
            self.typemap[shape_name] = types.containers.UniTuple(types.intp,
                                                               in_arr_typ.ndim)
            init_block.body.extend([ir.Assign(shape_getattr, shape_var, loc)])

            zero_name = ir_utils.mk_unique_var("zero_val")
            zero_var = ir.Var(scope, zero_name, loc)
            if "cval" in stencil_func.options:
                cval = stencil_func.options["cval"]
                # TODO: Loosen this restriction to adhere to casting rules.
                if return_type.dtype != typing.typeof.typeof(cval):
                    raise ValueError("cval type does not match stencil return type.")

                temp2 = return_type.dtype(cval)
            else:
                temp2 = return_type.dtype(0)
            full_const = ir.Const(temp2, loc)
            self.typemap[zero_name] = return_type.dtype
            init_block.body.extend([ir.Assign(full_const, zero_var, loc)])

            so_name = ir_utils.mk_unique_var("stencil_output")
            out_arr = ir.Var(scope, so_name, loc)
            self.typemap[out_arr.name] = numba.types.npytypes.Array(
                                                           return_type.dtype,
                                                           in_arr_typ.ndim,
                                                           in_arr_typ.layout)
            dtype_g_np_var = ir.Var(scope, mk_unique_var("$np_g_var"), loc)
            self.typemap[dtype_g_np_var.name] = types.misc.Module(np)
            dtype_g_np = ir.Global('np', np, loc)
            dtype_g_np_assign = ir.Assign(dtype_g_np, dtype_g_np_var, loc)
            init_block.body.append(dtype_g_np_assign)

            dtype_np_attr_call = ir.Expr.getattr(dtype_g_np_var, return_type.dtype.name, loc)
            dtype_attr_var = ir.Var(scope, mk_unique_var("$np_attr_attr"), loc)
            self.typemap[dtype_attr_var.name] = types.functions.NumberClass(return_type.dtype)
            dtype_attr_assign = ir.Assign(dtype_np_attr_call, dtype_attr_var, loc)
            init_block.body.append(dtype_attr_assign)

            stmts = ir_utils.gen_np_call("full",
                                       np.full,
                                       out_arr,
                                       [shape_var, zero_var, dtype_attr_var],
                                       self.typingctx,
                                       self.typemap,
                                       self.calltypes)
            equiv_set.insert_equiv(out_arr, in_arr_dim_sizes)
            init_block.body.extend(stmts)

        self.replace_return_with_setitem(stencil_blocks, exit_value_var,
                                         parfor_body_exit_label)

        if config.DEBUG_ARRAY_OPT == 1:
            print("stencil_blocks after replacing return")
            ir_utils.dump_blocks(stencil_blocks)

        setitem_call = ir.SetItem(out_arr, parfor_ind_var, exit_value_var, loc)
        self.calltypes[setitem_call] = signature(
                                        types.none, self.typemap[out_arr.name],
                                        self.typemap[parfor_ind_var.name],
                                        self.typemap[out_arr.name].dtype
                                        )
        stencil_blocks[parfor_body_exit_label].body.extend(for_replacing_ret)
        stencil_blocks[parfor_body_exit_label].body.append(setitem_call)

        # simplify CFG of parfor body (exit block could be simplified often)
        # add dummy return to enable CFG
        stencil_blocks[parfor_body_exit_label].body.append(ir.Return(0,
                                            ir.Loc("stencilparfor_dummy", -1)))
        stencil_blocks = ir_utils.simplify_CFG(stencil_blocks)
        stencil_blocks[max(stencil_blocks.keys())].body.pop()

        if config.DEBUG_ARRAY_OPT == 1:
            print("stencil_blocks after adding SetItem")
            ir_utils.dump_blocks(stencil_blocks)

        pattern = ('stencil', [start_lengths, end_lengths])
        parfor = numba.parfor.Parfor(loopnests, init_block, stencil_blocks,
                                     loc, parfor_ind_var, equiv_set, pattern, self.flags)
        gen_nodes.append(parfor)
        gen_nodes.append(ir.Assign(out_arr, target, loc))
        return gen_nodes