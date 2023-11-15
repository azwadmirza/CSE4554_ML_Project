    def forward(self, x1, x2):
        x1_, x2_ = self._create_input_grid(x1, x2)
        x1_ = x1_.div(self.period_length)
        x2_ = x2_.div(self.period_length)

        diff = torch.sum((x1_ - x2_).abs(), -1)
        res = torch.sin(diff.mul(math.pi)).pow(2).mul(-2 / self.lengthscale).exp_()
        return res