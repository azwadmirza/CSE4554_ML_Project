    def forward(self, x1, x2):
        x1_, x2_ = self._create_input_grid(x1, x2)
        x1_ = x1_.div(self.lengthscale)
        x2_ = x2_.div(self.lengthscale)

        diff = (x1_ - x2_).norm(2, dim=-1)
        return diff.pow(2).div_(-2).exp_()