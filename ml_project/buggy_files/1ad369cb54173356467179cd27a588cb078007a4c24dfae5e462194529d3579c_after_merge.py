    def time_to_anomaly(self, value):
        """Returns time required to be in a specific true anomaly.

        Parameters
        ----------
        value : ~astropy.units.Quantity

        Returns
        -------
        tof: ~astropy.units.Quantity
            Time of flight required.

        """
        # Silently wrap anomaly
        nu = (value + np.pi * u.rad) % (2 * np.pi * u.rad) - np.pi * u.rad

        delta_t = (
            delta_t_from_nu_fast(
                nu.to_value(u.rad),
                self.ecc.value,
                self.attractor.k.to_value(u.km ** 3 / u.s ** 2),
                self.r_p.to_value(u.km),
            )
            * u.s
        )
        tof = delta_t - self.t_p
        return tof