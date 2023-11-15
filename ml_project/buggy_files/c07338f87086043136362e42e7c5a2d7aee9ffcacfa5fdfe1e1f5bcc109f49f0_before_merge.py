    def run(self):
        """run parfor conversion pass: replace Numpy calls
        with Parfors when possible and optimize the IR."""

        self.array_analysis.run()
        topo_order = find_topo_order(self.func_ir.blocks)
        # variables available in the program so far (used for finding map
        # functions in array_expr lowering)
        avail_vars = []
        for label in topo_order:
            block = self.func_ir.blocks[label]
            new_body = []
            for instr in block.body:
                if isinstance(instr, ir.Assign):
                    expr = instr.value
                    lhs = instr.target
                    # only translate C order since we can't allocate F
                    if self._has_known_shape(lhs) and self._is_C_order(lhs.name):
                        if self._is_supported_npycall(expr):
                            instr = self._numpy_to_parfor(lhs, expr)
                        elif isinstance(expr, ir.Expr) and expr.op == 'arrayexpr':
                            instr = self._arrayexpr_to_parfor(lhs, expr, avail_vars)
                    elif self._is_supported_npyreduction(expr):
                        instr = self._reduction_to_parfor(lhs, expr)
                    avail_vars.append(lhs.name)
                new_body.append(instr)
            block.body = new_body

        # remove Del statements for easier optimization
        remove_dels(self.func_ir.blocks)
        dprint_func_ir(self.func_ir, "after parfor pass")
        # get copies in to blocks and out from blocks
        in_cps, out_cps = copy_propagate(self.func_ir.blocks, self.typemap)
        # table mapping variable names to ir.Var objects to help replacement
        name_var_table = get_name_var_table(self.func_ir.blocks)
        apply_copy_propagate(self.func_ir.blocks, in_cps, name_var_table,
            array_analysis.copy_propagate_update_analysis, self.array_analysis,
            self.typemap, self.calltypes)
        # remove dead code to enable fusion
        remove_dead(self.func_ir.blocks, self.func_ir.arg_names)
        #dprint_func_ir(self.func_ir, "after remove_dead")
        # reorder statements to maximize fusion
        maximize_fusion(self.func_ir.blocks)
        fuse_parfors(self.func_ir.blocks)
        # remove dead code after fusion to remove extra arrays and variables
        remove_dead(self.func_ir.blocks, self.func_ir.arg_names)
        #dprint_func_ir(self.func_ir, "after second remove_dead")
        # push function call variables inside parfors so gufunc function
        # wouldn't need function variables as argument
        push_call_vars(self.func_ir.blocks, {}, {})
        remove_dead(self.func_ir.blocks, self.func_ir.arg_names)
        # after optimization, some size variables are not available anymore
        remove_dead_class_sizes(self.func_ir.blocks, self.array_analysis)
        dprint_func_ir(self.func_ir, "after optimization")
        if config.DEBUG_ARRAY_OPT==1:
            print("variable types: ",sorted(self.typemap.items()))
            print("call types: ", self.calltypes)
        # run post processor again to generate Del nodes
        post_proc = postproc.PostProcessor(self.func_ir)
        post_proc.run()
        if self.func_ir.is_generator:
            fix_generator_types(self.func_ir.generator_info, self.return_type,
                self.typemap)
        #lower_parfor_sequential(self.func_ir, self.typemap, self.calltypes)
        return