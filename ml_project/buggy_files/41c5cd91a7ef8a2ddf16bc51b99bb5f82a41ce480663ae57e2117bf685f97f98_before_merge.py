    def lengthscale(self):
        if "log_lengthscale" in self.named_parameters().keys():
            return self.log_lengthscale.exp()
        else:
            return None