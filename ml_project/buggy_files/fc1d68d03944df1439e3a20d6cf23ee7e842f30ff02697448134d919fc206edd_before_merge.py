    def define_objectmode_pipeline(state, name='object'):
        """Returns an object-mode pipeline based PassManager
        """
        pm = PassManager(name)
        if state.func_ir is None:
            pm.add_pass(TranslateByteCode, "analyzing bytecode")
            pm.add_pass(FixupArgs, "fix up args")
        pm.add_pass(IRProcessing, "processing IR")

        pm.add_pass(ObjectModeFrontEnd, "object mode frontend")
        pm.add_pass(InlineClosureLikes,
                    "inline calls to locally defined closures")
        # convert any remaining closures into functions
        pm.add_pass(MakeFunctionToJitFunction,
                    "convert make_function into JIT functions")
        pm.add_pass(AnnotateTypes, "annotate types")
        pm.add_pass(IRLegalization, "ensure IR is legal prior to lowering")
        pm.add_pass(ObjectModeBackEnd, "object mode backend")
        pm.finalize()
        return pm