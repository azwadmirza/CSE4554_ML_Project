    def _generate_time_values(self, nu_vals):
        # Subtract current anomaly to start from the desired point
        ecc = self.ecc.value
        nu = self.nu.to(u.rad).value

        M_vals = [
            nu_to_M_fast(nu_val, ecc) - nu_to_M_fast(nu, ecc)
            for nu_val in nu_vals.to(u.rad).value
        ] * u.rad

        time_values = (M_vals / self.n).decompose()
        return time_values