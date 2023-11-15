    def get_function(self):
        def equal_scalar(vals):
            return pd.Series(vals) == self.value
        return equal_scalar