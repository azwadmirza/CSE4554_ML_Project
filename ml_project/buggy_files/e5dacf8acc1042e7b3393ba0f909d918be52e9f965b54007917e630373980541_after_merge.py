    def lower_call(self, resty, expr):
        signature = self.fndesc.calltypes[expr]
        self.debug_print("# lower_call: expr = {0}".format(expr))
        if isinstance(signature.return_type, types.Phantom):
            return self.context.get_dummy_value()

        fnty = self.typeof(expr.func.name)

        if isinstance(fnty, types.ObjModeDispatcher):
            res = self._lower_call_ObjModeDispatcher(fnty, expr, signature)

        elif isinstance(fnty, types.ExternalFunction):
            res = self._lower_call_ExternalFunction(fnty, expr, signature)

        elif isinstance(fnty, types.ExternalFunctionPointer):
            res = self._lower_call_ExternalFunctionPointer(
                fnty, expr, signature)

        elif isinstance(fnty, types.RecursiveCall):
            res = self._lower_call_RecursiveCall(fnty, expr, signature)

        elif isinstance(fnty, types.FunctionType):
            res = self._lower_call_FunctionType(fnty, expr, signature)

        else:
            res = self._lower_call_normal(fnty, expr, signature)

        # If lowering the call returned None, interpret that as returning dummy
        # value if the return type of the function is void, otherwise there is
        # a problem
        if res is None:
            if signature.return_type == types.void:
                res = self.context.get_dummy_value()
            else:
                raise LoweringError(
                    msg="non-void function returns None from implementation",
                    loc=self.loc
                )

        return self.context.cast(self.builder, res, signature.return_type,
                                 resty)