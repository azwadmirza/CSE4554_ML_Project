    def forward_diag(self, x1, x2):
        mean = x1.mean(1, keepdim=True).mean(0, keepdim=True)
        x1_normed = x1 - mean.unsqueeze(0).unsqueeze(1)
        x2_normed = x2 - mean.unsqueeze(0).unsqueeze(1)

        diff = x1_normed - x2_normed
        distance_over_rho = diff.pow_(2).sum(-1).sqrt()
        exp_component = torch.exp(-math.sqrt(self.nu * 2) * distance_over_rho)

        if self.nu == 0.5:
            constant_component = 1
        elif self.nu == 1.5:
            constant_component = (math.sqrt(3) * distance_over_rho).add(1)
        elif self.nu == 2.5:
            constant_component = (math.sqrt(5) * distance_over_rho).add(1).add(5. / 3. * distance_over_rho ** 2)

        return constant_component * exp_component