    def _fail(self, val):
        # The location here is set to None because `val` is the ir.Var name
        # and not the actual offending use of the var. When this is raised it is
        # caught in the flow control of `infer_constant` and the class and args
        # (the message) are captured and then raised again but with the location
        # set to the expression that caused the constant inference error.
        raise ConstantInferenceError(
            "Constant inference not possible for: %s" % (val,), loc=None)