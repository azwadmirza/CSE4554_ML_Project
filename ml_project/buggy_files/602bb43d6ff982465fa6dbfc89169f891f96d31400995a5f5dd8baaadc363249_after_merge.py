    def codegen(context, builder, signature, args):
        [src] = args
        return builder.ctlz(src, ir.Constant(ir.IntType(1), 0))