    def attach_columns(self, result):
        if result.squeeze().ndim <= 1:
            return Series(result, index=self.xnames)
        else: # for e.g., confidence intervals
            return DataFrame(result, index=self.xnames)