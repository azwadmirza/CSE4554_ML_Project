    def t_p(self):
        """Elapsed time since latest perifocal passage. """
        M = nu_to_M_fast(self.nu.to_value(u.rad), self.ecc.value) * u.rad
        t_p = self.period * M / (360 * u.deg)
        return t_p