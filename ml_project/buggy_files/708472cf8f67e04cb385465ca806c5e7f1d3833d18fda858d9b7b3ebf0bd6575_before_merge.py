    def _generate_time_values(self, nu_vals):
        M_vals = nu_to_M(nu_vals, self.ecc)
        time_values = self.epoch + (M_vals / self.n).decompose()
        return time_values