    def lower_assign(self, ty, inst):
        value = inst.value
        # In nopython mode, closure vars are frozen like globals
        if isinstance(value, (ir.Const, ir.Global, ir.FreeVar)):
            res = self.context.get_constant_generic(self.builder, ty,
                                                    value.value)
            self.incref(ty, res)
            return res

        elif isinstance(value, ir.Expr):
            return self.lower_expr(ty, value)

        elif isinstance(value, ir.Var):
            val = self.loadvar(value.name)
            oty = self.typeof(value.name)
            res = self.context.cast(self.builder, val, oty, ty)
            self.incref(ty, res)
            return res

        elif isinstance(value, ir.Arg):
            # Cast from the argument type to the local variable type
            # (note the "arg.FOO" convention as used in typeinfer)
            argty = self.typeof("arg." + value.name)
            if isinstance(argty, types.Omitted):
                pyval = argty.value
                tyctx = self.context.typing_context
                valty = tyctx.resolve_value_type_prefer_literal(pyval)
                # use the type of the constant value
                const = self.context.get_constant_generic(
                    self.builder, valty, pyval,
                )
                # cast it to the variable type
                res = self.context.cast(self.builder, const, valty, ty)
            else:
                val = self.fnargs[value.index]
                res = self.context.cast(self.builder, val, argty, ty)
            self.incref(ty, res)
            return res

        elif isinstance(value, ir.Yield):
            res = self.lower_yield(ty, value)
            self.incref(ty, res)
            return res

        raise NotImplementedError(type(value), value)