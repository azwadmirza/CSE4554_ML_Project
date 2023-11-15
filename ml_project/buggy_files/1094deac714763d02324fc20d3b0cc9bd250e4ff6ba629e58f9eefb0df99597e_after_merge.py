    def _kinetic_energy(self, r):
        # TODO: revert to `torch.dot` in pytorch==1.0
        # See: https://github.com/uber/pyro/issues/1458
        r_flat = torch.cat([r[site_name].reshape(-1) for site_name in sorted(r)])
        if self.full_mass:
            return 0.5 * (r_flat * (self._inverse_mass_matrix.matmul(r_flat))).sum()
        else:
            return 0.5 * (self._inverse_mass_matrix * (r_flat ** 2)).sum()