    def call_function_pointer(self, builder, funcptr, signature, args):
        retty = self.get_value_type(signature.return_type)
        fnty = Type.function(retty, [a.type for a in args])
        fnptrty = Type.pointer(fnty)
        addr = self.get_constant(types.intp, funcptr)
        ptr = builder.inttoptr(addr, fnptrty)
        return builder.call(ptr, args)