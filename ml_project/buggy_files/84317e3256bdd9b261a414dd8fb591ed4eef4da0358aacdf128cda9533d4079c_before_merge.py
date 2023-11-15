    def _fail(self, val):
        raise ConstantInferenceError(
            "constant inference not possible for %s" % (val,))