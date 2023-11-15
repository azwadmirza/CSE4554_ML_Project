    def forward(self, x1, x2):
        mean = x1.view(-1, 1, *list(x1.size())[2:]).mean(0, keepdim=True)
        x1_, x2_ = self._create_input_grid(x1 - mean, x2 - mean)
        x1_ = x1_.div(self.lengthscale)
        x2_ = x2_.div(self.lengthscale)

        distance = (x1_ - x2_).norm(2, dim=-1)
        exp_component = torch.exp(-math.sqrt(self.nu * 2) * distance)

        if self.nu == 0.5:
            constant_component = 1
        elif self.nu == 1.5:
            constant_component = (math.sqrt(3) * distance).add(1)
        elif self.nu == 2.5:
            constant_component = (math.sqrt(5) * distance).add(1).add(5. / 3. * distance ** 2)
        return constant_component * exp_component