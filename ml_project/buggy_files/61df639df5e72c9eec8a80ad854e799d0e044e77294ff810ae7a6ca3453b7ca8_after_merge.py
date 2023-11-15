    def __init__(self, func_ir, typemap, calltypes, return_type, typingctx):
        self.func_ir = func_ir
        self.typemap = typemap
        self.calltypes = calltypes
        self.typingctx = typingctx
        self.return_type = return_type
        self.array_analysis = array_analysis.ArrayAnalysis(func_ir, typemap,
                                                           calltypes)
        ir_utils._max_label = max(func_ir.blocks.keys())