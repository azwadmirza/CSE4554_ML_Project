    def __init__(self, value, loc=None):
        self.value = value
        msg = "Cannot make a constant from: %s" % value
        super(ConstantInferenceError, self).__init__(msg, loc=loc)