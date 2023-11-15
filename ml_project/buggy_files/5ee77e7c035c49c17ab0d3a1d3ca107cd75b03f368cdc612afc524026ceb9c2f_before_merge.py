    def _numpy_to_parfor(self, lhs, expr):
        assert isinstance(expr, ir.Expr) and expr.op == 'call'
        call_name = self.array_analysis.numpy_calls[expr.func.name]
        args = expr.args
        kws = dict(expr.kws)
        if call_name in ['zeros', 'ones', 'random.ranf']:
            return self._numpy_map_to_parfor(call_name, lhs, args, kws, expr)
        if call_name=='dot':
            assert len(args)==2 or len(args)==3
            # if 3 args, output is allocated already
            out = None
            if len(args)==3:
                out = args[2]
            if 'out' in kws:
                out = kws['out']

            in1 = args[0]
            in2 = args[1]
            el_typ = self.typemap[lhs.name].dtype
            assert self._get_ndims(in1.name)<=2 and self._get_ndims(in2.name)==1
            # loop range correlation is same as first dimention of 1st input
            corr = self.array_analysis.array_shape_classes[in1.name][0]
            size_var = self.array_analysis.array_size_vars[in1.name][0]
            scope = lhs.scope
            loc = expr.loc
            index_var = ir.Var(scope, mk_unique_var("parfor_index"), lhs.loc)
            self.typemap[index_var.name] = types.intp
            loopnests = [ LoopNest(index_var, 0, size_var, 1, corr) ]
            init_block = ir.Block(scope, loc)
            parfor = Parfor(loopnests, init_block, {}, loc, self.array_analysis, index_var)
            if self._get_ndims(in1.name)==2:
                # for 2D input, there is an inner loop
                # correlation of inner dimension
                inner_size_var = self.array_analysis.array_size_vars[in1.name][1]
                # loop structure: range block, header block, body

                range_label = next_label()
                header_label = next_label()
                body_label = next_label()
                out_label = next_label()

                if out==None:
                    alloc_nodes = mk_alloc(self.typemap, self.calltypes, lhs,
                        size_var, el_typ, scope, loc)
                    init_block.body = alloc_nodes
                else:
                    out_assign = ir.Assign(out, lhs, loc)
                    init_block.body = [out_assign]
                init_block.body.extend(_gen_dotmv_check(self.typemap,
                    self.calltypes, in1, in2, lhs, scope, loc))
                # sum_var = 0
                const_node = ir.Const(0, loc)
                const_var = ir.Var(scope, mk_unique_var("$const"), loc)
                self.typemap[const_var.name] = el_typ
                const_assign = ir.Assign(const_node, const_var, loc)
                sum_var = ir.Var(scope, mk_unique_var("$sum_var"), loc)
                self.typemap[sum_var.name] = el_typ
                sum_assign = ir.Assign(const_var, sum_var, loc)

                range_block = mk_range_block(self.typemap, 0, inner_size_var, 1,
                    self.calltypes, scope, loc)
                range_block.body = [const_assign, sum_assign] + range_block.body
                range_block.body[-1].target = header_label # fix jump target
                phi_var = range_block.body[-2].target

                header_block = mk_loop_header(self.typemap, phi_var,
                    self.calltypes, scope, loc)
                header_block.body[-1].truebr = body_label
                header_block.body[-1].falsebr = out_label
                phi_b_var = header_block.body[-2].target

                body_block = _mk_mvdot_body(self.typemap, self.calltypes,
                    phi_b_var, index_var, in1, in2,
                    sum_var, scope, loc, el_typ)
                body_block.body[-1].target = header_label

                out_block = ir.Block(scope, loc)
                # lhs[parfor_index] = sum_var
                setitem_node = ir.SetItem(lhs, index_var, sum_var, loc)
                self.calltypes[setitem_node] = signature(types.none,
                    self.typemap[lhs.name], types.intp, el_typ)
                out_block.body = [setitem_node]
                parfor.loop_body = {range_label:range_block,
                    header_label:header_block, body_label:body_block,
                    out_label:out_block}
            else: # self._get_ndims(in1.name)==1 (reduction)
                NotImplementedError("no reduction for dot() "+expr)
            if config.DEBUG_ARRAY_OPT==1:
                print("generated parfor for numpy call:")
                parfor.dump()
            return parfor
        # return error if we couldn't handle it (avoid rewrite infinite loop)
        raise NotImplementedError("parfor translation failed for ", expr)