    def __init__(self, value, options):
        self.value = as_value_expr(value)
        self.options = as_value_expr(options)
        super(Contains, self).__init__(self.value, self.options)