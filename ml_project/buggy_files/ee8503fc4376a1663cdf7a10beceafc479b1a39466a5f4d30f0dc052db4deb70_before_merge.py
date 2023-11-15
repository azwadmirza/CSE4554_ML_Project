    def forward(self, x1, x2):
        lengthscale = (self.log_lengthscale.exp() + self.eps).sqrt_()
        period_length = (self.log_period_length.exp() + self.eps).sqrt_()
        diff = torch.sum((x1.unsqueeze(2) - x2.unsqueeze(1)).abs(), -1)
        res = -2 * torch.sin(math.pi * diff / period_length).pow(2) / lengthscale
        return res.exp()