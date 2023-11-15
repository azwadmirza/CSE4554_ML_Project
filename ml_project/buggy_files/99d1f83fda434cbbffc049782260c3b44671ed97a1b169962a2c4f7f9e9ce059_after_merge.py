    def _numpy_map_to_parfor(self, call_name, lhs, args, kws, expr):
        """generate parfor from Numpy calls that are maps.
        """
        scope = lhs.scope
        loc = lhs.loc
        arr_typ = self.typemap[lhs.name]
        el_typ = arr_typ.dtype

        # generate loopnests and size variables from lhs correlations
        loopnests = []
        size_vars = []
        index_vars = []
        for this_dim in range(arr_typ.ndim):
            corr = self.array_analysis.array_shape_classes[lhs.name][this_dim]
            size_var = self.array_analysis.array_size_vars[lhs.name][this_dim]
            size_vars.append(size_var)
            index_var = ir.Var(scope, mk_unique_var("parfor_index"), loc)
            index_vars.append(index_var)
            self.typemap[index_var.name] = types.intp
            loopnests.append(LoopNest(index_var, 0, size_var, 1, corr))

        # generate init block and body
        init_block = ir.Block(scope, loc)
        init_block.body = mk_alloc(self.typemap, self.calltypes, lhs,
                                   tuple(size_vars), el_typ, scope, loc)
        body_label = next_label()
        body_block = ir.Block(scope, loc)
        expr_out_var = ir.Var(scope, mk_unique_var("$expr_out_var"), loc)
        self.typemap[expr_out_var.name] = el_typ

        index_var, index_var_typ = self._make_index_var(
            scope, index_vars, body_block)

        if call_name == 'zeros':
            value = ir.Const(0, loc)
        elif call_name == 'ones':
            value = ir.Const(1, loc)
        elif call_name.startswith('random.'):
            # remove size arg to reuse the call expr for single value
            _remove_size_arg(call_name, expr)
            # update expr type
            new_arg_typs, new_kw_types = _get_call_arg_types(
                expr, self.typemap)
            self.calltypes.pop(expr)
            self.calltypes[expr] = self.typemap[expr.func.name].get_call_type(
                typing.Context(), new_arg_typs, new_kw_types)
            value = expr
        else:
            NotImplementedError(
                "Map of numpy.{} to parfor is not implemented".format(call_name))

        value_assign = ir.Assign(value, expr_out_var, loc)
        body_block.body.append(value_assign)

        parfor = Parfor(
            loopnests,
            init_block,
            {},
            loc,
            self.array_analysis,
            index_var)

        setitem_node = ir.SetItem(lhs, index_var, expr_out_var, loc)
        self.calltypes[setitem_node] = signature(
            types.none, self.typemap[lhs.name], index_var_typ, el_typ)
        body_block.body.append(setitem_node)
        parfor.loop_body = {body_label: body_block}
        if config.DEBUG_ARRAY_OPT == 1:
            print("generated parfor for numpy map:")
            parfor.dump()
        return parfor