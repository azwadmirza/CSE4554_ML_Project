    def run(self):
        """run parfor conversion pass: replace Numpy calls
        with Parfors when possible and optimize the IR."""
        self.func_ir.blocks = simplify_CFG(self.func_ir.blocks)
        # remove Del statements for easier optimization
        remove_dels(self.func_ir.blocks)
        # e.g. convert A.sum() to np.sum(A) for easier match and optimization
        canonicalize_array_math(self.func_ir.blocks, self.typemap,
                                self.calltypes, self.typingctx)
        self.array_analysis.run()
        self._convert_prange(self.func_ir.blocks)
        self._convert_numpy(self.func_ir.blocks)

        dprint_func_ir(self.func_ir, "after parfor pass")
        simplify(self.func_ir, self.typemap, self.array_analysis,
                 self.calltypes, array_analysis.copy_propagate_update_analysis)

        #dprint_func_ir(self.func_ir, "after remove_dead")
        # reorder statements to maximize fusion
        maximize_fusion(self.func_ir.blocks)
        fuse_parfors(self.func_ir.blocks)
        # remove dead code after fusion to remove extra arrays and variables
        remove_dead(self.func_ir.blocks, self.func_ir.arg_names, self.typemap)
        #dprint_func_ir(self.func_ir, "after second remove_dead")
        # push function call variables inside parfors so gufunc function
        # wouldn't need function variables as argument
        push_call_vars(self.func_ir.blocks, {}, {})
        remove_dead(self.func_ir.blocks, self.func_ir.arg_names, self.typemap)
        # after optimization, some size variables are not available anymore
        remove_dead_class_sizes(self.func_ir.blocks, self.array_analysis)
        dprint_func_ir(self.func_ir, "after optimization")
        if config.DEBUG_ARRAY_OPT == 1:
            print("variable types: ", sorted(self.typemap.items()))
            print("call types: ", self.calltypes)
        # run post processor again to generate Del nodes
        post_proc = postproc.PostProcessor(self.func_ir)
        post_proc.run()
        if self.func_ir.is_generator:
            fix_generator_types(self.func_ir.generator_info, self.return_type,
                                self.typemap)
        if sequential_parfor_lowering:
            lower_parfor_sequential(self.func_ir, self.typemap, self.calltypes)
        else:
            # prepare for parallel lowering
            # add parfor params to parfors here since lowering is destructive
            # changing the IR after this is not allowed
            get_parfor_params(self.func_ir.blocks)
        return