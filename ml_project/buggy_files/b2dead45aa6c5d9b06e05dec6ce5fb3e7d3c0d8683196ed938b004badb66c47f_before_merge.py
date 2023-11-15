    def __init__(self, value, options):
        self.value = as_value_expr(value)
        self.options = as_value_expr(options)
        BooleanValueOp.__init__(self, self.value, self.options)