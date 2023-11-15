    def _generate_time_values(self, nu_vals):
        # Subtract current anomaly to start from the desired point
        ecc = self.ecc.value
        k = self.attractor.k.to_value(u.km ** 3 / u.s ** 2)
        q = self.r_p.to_value(u.km)

        time_values = [
            delta_t_from_nu_fast(nu_val, ecc, k, q)
            for nu_val in nu_vals.to(u.rad).value
        ] * u.s - self.t_p
        return time_values