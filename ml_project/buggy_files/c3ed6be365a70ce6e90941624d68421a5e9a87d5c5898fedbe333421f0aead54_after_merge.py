    def run(self):
        """run parfor conversion pass: replace Numpy calls
        with Parfors when possible and optimize the IR."""
        # run array analysis, a pre-requisite for parfor translation
        remove_dels(self.func_ir.blocks)
        self.array_analysis.run(self.func_ir.blocks)
        # run stencil translation to parfor
        if self.options.stencil:
            stencil_pass = StencilPass(self.func_ir, self.typemap, self.calltypes,
                                            self.array_analysis, self.typingctx, self.flags)
            stencil_pass.run()
        if self.options.setitem:
            self._convert_setitem(self.func_ir.blocks)
        if self.options.numpy:
            self._convert_numpy(self.func_ir.blocks)
        if self.options.reduction:
            self._convert_reduce(self.func_ir.blocks)
        if self.options.prange:
           self._convert_loop(self.func_ir.blocks)

        # setup diagnostics now parfors are found
        self.diagnostics.setup(self.func_ir, self.options.fusion)

        dprint_func_ir(self.func_ir, "after parfor pass")

        # simplify CFG of parfor body loops since nested parfors with extra
        # jumps can be created with prange conversion
        simplify_parfor_body_CFG(self.func_ir.blocks)
        # simplify before fusion
        simplify(self.func_ir, self.typemap, self.calltypes)
        # need two rounds of copy propagation to enable fusion of long sequences
        # of parfors like test_fuse_argmin (some PYTHONHASHSEED values since
        # apply_copies_parfor depends on set order for creating dummy assigns)
        simplify(self.func_ir, self.typemap, self.calltypes)

        if self.options.fusion:
            self.func_ir._definitions = build_definitions(self.func_ir.blocks)
            self.array_analysis.equiv_sets = dict()
            self.array_analysis.run(self.func_ir.blocks)
            # reorder statements to maximize fusion
            # push non-parfors down
            maximize_fusion(self.func_ir, self.func_ir.blocks, self.typemap,
                                                            up_direction=False)
            dprint_func_ir(self.func_ir, "after maximize fusion down")
            self.fuse_parfors(self.array_analysis, self.func_ir.blocks)
            # push non-parfors up
            maximize_fusion(self.func_ir, self.func_ir.blocks, self.typemap)
            dprint_func_ir(self.func_ir, "after maximize fusion up")
            # try fuse again after maximize
            self.fuse_parfors(self.array_analysis, self.func_ir.blocks)
            dprint_func_ir(self.func_ir, "after fusion")
        # simplify again
        simplify(self.func_ir, self.typemap, self.calltypes)
        # push function call variables inside parfors so gufunc function
        # wouldn't need function variables as argument
        push_call_vars(self.func_ir.blocks, {}, {})
        # simplify again
        simplify(self.func_ir, self.typemap, self.calltypes)
        dprint_func_ir(self.func_ir, "after optimization")
        if config.DEBUG_ARRAY_OPT >= 1:
            print("variable types: ", sorted(self.typemap.items()))
            print("call types: ", self.calltypes)
        # run post processor again to generate Del nodes
        post_proc = postproc.PostProcessor(self.func_ir)
        post_proc.run()
        if self.func_ir.is_generator:
            fix_generator_types(self.func_ir.generator_info, self.return_type,
                                self.typemap)
        if sequential_parfor_lowering:
            lower_parfor_sequential(
                self.typingctx, self.func_ir, self.typemap, self.calltypes)
        else:
            # prepare for parallel lowering
            # add parfor params to parfors here since lowering is destructive
            # changing the IR after this is not allowed
            parfor_ids, parfors = get_parfor_params(self.func_ir.blocks,
                                                    self.options.fusion,
                                                    self.nested_fusion_info)
            for p in parfors:
                numba.parfor.get_parfor_reductions(self.func_ir,
                                                   p,
                                                   p.params,
                                                   self.calltypes)
            if config.DEBUG_ARRAY_OPT_STATS:
                name = self.func_ir.func_id.func_qualname
                n_parfors = len(parfor_ids)
                if n_parfors > 0:
                    after_fusion = ("After fusion" if self.options.fusion
                                    else "With fusion disabled")
                    print(('{}, function {} has '
                           '{} parallel for-loop(s) #{}.').format(
                           after_fusion, name, n_parfors, parfor_ids))
                else:
                    print('Function {} has no Parfor.'.format(name))

        return