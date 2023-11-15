    def attach_cov(self, result):
        return DataFrame(result, index=self.param_names,
                         columns=self.param_names)