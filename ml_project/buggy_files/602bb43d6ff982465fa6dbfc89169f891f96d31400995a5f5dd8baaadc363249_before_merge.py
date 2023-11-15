    def codegen(cgctx, builder, typ, args):
        flt = args[0]
        return builder.bitcast(flt, bitcastty)