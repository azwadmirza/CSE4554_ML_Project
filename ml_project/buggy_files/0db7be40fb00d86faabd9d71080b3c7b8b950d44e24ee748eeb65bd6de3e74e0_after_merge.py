    def attach_cov(self, result):
        return DataFrame(result, index=self.cov_names, columns=self.cov_names)