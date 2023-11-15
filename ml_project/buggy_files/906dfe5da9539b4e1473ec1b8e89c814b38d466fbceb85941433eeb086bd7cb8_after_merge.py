    def getattr_value(self, val):
        if isinstance(val, string_types):
            val = getattr(self, val)

        if isinstance(val, tt.TensorVariable):
            return val.tag.test_value

        if isinstance(val, tt.sharedvar.SharedVariable):
            return val.get_value()

        if isinstance(val, theano_constant):
            return val.value

        return val