    def lengthscale(self):
        if self.has_lengthscale:
            return self.log_lengthscale.exp().clamp(self.eps, 1e5)
        else:
            return None