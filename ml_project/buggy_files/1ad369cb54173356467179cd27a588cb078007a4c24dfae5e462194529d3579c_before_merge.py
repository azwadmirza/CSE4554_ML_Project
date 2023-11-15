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
        # Compute time of flight for correct epoch
        M = nu_to_M_fast(self.nu.to_value(u.rad), self.ecc.value) * u.rad
        new_M = nu_to_M_fast(value.to_value(u.rad), self.ecc.value) * u.rad
        tof = Angle(new_M - M).wrap_at(360 * u.deg) / self.n

        return tof