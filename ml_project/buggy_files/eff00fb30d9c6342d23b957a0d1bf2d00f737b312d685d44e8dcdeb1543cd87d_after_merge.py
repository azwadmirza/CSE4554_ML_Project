    def _reduction_to_parfor(self, lhs, expr):
        assert isinstance(expr, ir.Expr) and expr.op == 'call'
        call_name = self.array_analysis.numpy_calls[expr.func.name]
        args = expr.args
        kws = dict(expr.kws)
        if call_name in _reduction_ops:
            acc_op, im_op, init_val = _reduction_ops[call_name]
            assert len(args) in [1, 2]  # vector dot has 2 args
            in1 = args[0]
            arr_typ = self.typemap[in1.name]
            in_typ = arr_typ.dtype
            im_op_func_typ = find_op_typ(im_op, [in_typ, in_typ])
            el_typ = im_op_func_typ.return_type
            ndims = arr_typ.ndim

            # For full reduction, loop range correlation is same as 1st input
            corrs = self.array_analysis.array_shape_classes[in1.name]
            sizes = self.array_analysis.array_size_vars[in1.name]
            assert ndims == len(sizes) and ndims == len(corrs)
            scope = lhs.scope
            loc = expr.loc
            loopnests = []
            parfor_index = []
            for i in range(ndims):
                index_var = ir.Var(
                    scope, mk_unique_var(
                        "$parfor_index" + str(i)), loc)
                self.typemap[index_var.name] = types.intp
                parfor_index.append(index_var)
                loopnests.append(LoopNest(index_var, 0, sizes[i], 1, corrs[i]))

            acc_var = lhs

            # init value
            init_const = ir.Const(el_typ(init_val), loc)

            # init block has to init the reduction variable
            init_block = ir.Block(scope, loc)
            init_block.body.append(ir.Assign(init_const, acc_var, loc))

            # loop body accumulates acc_var
            acc_block = ir.Block(scope, loc)
            tmp_var = ir.Var(scope, mk_unique_var("$val"), loc)
            self.typemap[tmp_var.name] = in_typ
            index_var, index_var_type = self._make_index_var(
                scope, parfor_index, acc_block)
            getitem_call = ir.Expr.getitem(in1, index_var, loc)
            self.calltypes[getitem_call] = signature(
                in_typ, arr_typ, index_var_type)
            acc_block.body.append(ir.Assign(getitem_call, tmp_var, loc))

            if call_name is 'dot':
                # dot has two inputs
                tmp_var1 = tmp_var
                in2 = args[1]
                tmp_var2 = ir.Var(scope, mk_unique_var("$val"), loc)
                self.typemap[tmp_var2.name] = in_typ
                getitem_call2 = ir.Expr.getitem(in2, index_var, loc)
                self.calltypes[getitem_call2] = signature(
                    in_typ, arr_typ, index_var_type)
                acc_block.body.append(ir.Assign(getitem_call2, tmp_var2, loc))
                mult_call = ir.Expr.binop('*', tmp_var1, tmp_var2, loc)
                mult_func_typ = find_op_typ('*', [in_typ, in_typ])
                self.calltypes[mult_call] = mult_func_typ
                tmp_var = ir.Var(scope, mk_unique_var("$val"), loc)
                acc_block.body.append(ir.Assign(mult_call, tmp_var, loc))

            acc_call = ir.Expr.inplace_binop(
                acc_op, im_op, acc_var, tmp_var, loc)
            # for some reason, type template of += returns None,
            # so type template of + should be used
            self.calltypes[acc_call] = im_op_func_typ
            # FIXME: we had to break assignment: acc += ... acc ...
            # into two assignment: acc_tmp = ... acc ...; x = acc_tmp
            # in order to avoid an issue in copy propagation.
            acc_tmp_var = ir.Var(scope, mk_unique_var("$acc"), loc)
            self.typemap[acc_tmp_var.name] = el_typ
            acc_block.body.append(ir.Assign(acc_call, acc_tmp_var, loc))
            acc_block.body.append(ir.Assign(acc_tmp_var, acc_var, loc))
            loop_body = {next_label(): acc_block}

            # parfor
            parfor = Parfor(loopnests, init_block, loop_body, loc,
                            self.array_analysis, index_var)
            return parfor
        # return error if we couldn't handle it (avoid rewrite infinite loop)
        raise NotImplementedError("parfor translation failed for ", expr)