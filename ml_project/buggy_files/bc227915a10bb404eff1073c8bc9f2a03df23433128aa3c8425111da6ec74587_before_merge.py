    def run_pass(self, state):
        # Determine whether to even attempt this pass... if there's no
        # `literal_unroll as a global or as a freevar then just skip.
        found = False
        func_ir = state.func_ir
        for blk in func_ir.blocks.values():
            for asgn in blk.find_insts(ir.Assign):
                if isinstance(asgn.value, (ir.Global, ir.FreeVar)):
                    if asgn.value.value is literal_unroll:
                        found = True
                        break
            if found:
                break
        if not found:
            return False

        # run as subpipeline
        from numba.core.compiler_machinery import PassManager
        from numba.core.typed_passes import PartialTypeInference
        pm = PassManager("literal_unroll_subpipeline")
        # get types where possible to help with list->tuple change
        pm.add_pass(PartialTypeInference, "performs partial type inference")
        # make const lists tuples
        pm.add_pass(TransformLiteralUnrollConstListToTuple,
                    "switch const list for tuples")
        # recompute partial typemap following IR change
        pm.add_pass(PartialTypeInference, "performs partial type inference")
        # canonicalise loops
        pm.add_pass(IterLoopCanonicalization,
                    "switch iter loops for range driven loops")
        # rewrite consts
        pm.add_pass(RewriteSemanticConstants, "rewrite semantic constants")
        # do the unroll
        pm.add_pass(MixedContainerUnroller, "performs mixed container unroll")
        pm.finalize()
        pm.run(state)
        return True