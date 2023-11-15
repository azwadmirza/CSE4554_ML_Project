    def forward(self, x1, x2, diag=False, **params):
        x1_ = x1.div(self.period_length)
        x2_ = x2.div(self.period_length)
        diff = self.covar_dist(x1_, x2_, diag=diag, **params)
        res = torch.sin(diff.mul(math.pi)).pow(2).mul(-2 / self.lengthscale).exp_()
        if diag:
            res = res.squeeze(0)
        return res