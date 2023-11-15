    def _expand_callable_macro(self, func_ir, call, macro, loc):
        """
        Return the IR expression of expanding the macro call.
        """
        assert macro.callable

        # Resolve all macro arguments as constants, or fail
        args = [func_ir.infer_constant(arg.name) for arg in call.args]
        kws = {}
        for k, v in call.kws:
            try:
                kws[k] = func_ir.infer_constant(v)
            except errors.ConstantInferenceError:
                msg = "Argument {name!r} must be a " \
                      "constant at {loc}".format(name=k,
                                                 loc=loc)
                raise ValueError(msg)

        try:
            result = macro.func(*args, **kws)
        except Exception as e:
            msg = str(e)
            headfmt = "Macro expansion failed at {line}"
            head = headfmt.format(line=loc)
            newmsg = "{0}:\n{1}".format(head, msg)
            raise errors.MacroError(newmsg)

        assert result is not None

        result.loc = call.loc
        new_expr = ir.Expr.call(func=result, args=call.args,
                                kws=call.kws, loc=loc)
        return new_expr