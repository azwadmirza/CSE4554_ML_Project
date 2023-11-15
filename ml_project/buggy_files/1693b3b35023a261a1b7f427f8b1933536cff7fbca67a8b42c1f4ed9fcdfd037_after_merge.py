    def t_p(self):
        """Elapsed time since latest perifocal passage. """
        t_p = (
            delta_t_from_nu_fast(
                self.nu.to_value(u.rad),
                self.ecc.value,
                self.attractor.k.to_value(u.km ** 3 / u.s ** 2),
                self.r_p.to_value(u.km),
            )
            * u.s
        )
        return t_p