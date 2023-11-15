    def _generate_time_values(self, nu_vals):
        # Subtract current anomaly to start from the desired point
        M_vals = nu_to_M(nu_vals, self.ecc) - nu_to_M(self.nu, self.ecc)
        time_values = self.epoch + (M_vals / self.n).decompose()
        return time_values