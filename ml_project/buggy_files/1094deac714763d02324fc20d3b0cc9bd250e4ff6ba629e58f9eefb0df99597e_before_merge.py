    def _kinetic_energy(self, r):
        r_flat = torch.cat([r[site_name].reshape(-1) for site_name in sorted(r)])
        if self.full_mass:
            return 0.5 * r_flat.dot(self._inverse_mass_matrix.matmul(r_flat))
        else:
            return 0.5 * self._inverse_mass_matrix.dot(r_flat ** 2)