        def equal_scalar(vals):
            # case to correct pandas type for comparison
            return pd.Series(vals).astype(pd.Series([self.value]).dtype) == self.value