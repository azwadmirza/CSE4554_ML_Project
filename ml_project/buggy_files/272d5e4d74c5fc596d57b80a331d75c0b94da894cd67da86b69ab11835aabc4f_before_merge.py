    def forward(self, x1, x2):
        lengthscales = self.log_lengthscale.exp().mul(math.sqrt(2)).clamp(self.eps, 1e5)
        diff = (x1.unsqueeze(2) - x2.unsqueeze(1)).div_(lengthscales.unsqueeze(1))
        return diff.pow_(2).sum(-1).mul_(-1).exp_()