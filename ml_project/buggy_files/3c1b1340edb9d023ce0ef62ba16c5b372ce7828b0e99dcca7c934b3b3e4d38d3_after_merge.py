    def get_function(self):
        def not_equal_scalar(vals):
            return pd.Series(vals) != self.value
        return not_equal_scalar