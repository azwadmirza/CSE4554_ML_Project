    def _assert_can_compare(self):
        expr, lower, upper = self.args
        if not expr._can_compare(lower) or not expr._can_compare(upper):
            raise TypeError('Arguments are not comparable')