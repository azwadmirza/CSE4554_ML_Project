    def propagate_to_anomaly(self, value):
        """Propagates an orbit to a specific true anomaly.

        Parameters
        ----------
        value : ~astropy.units.Quantity

        Returns
        -------
        Orbit
            Resulting orbit after propagation.

        """

        # Compute time of flight for correct epoch
        time_of_flight = self.time_to_anomaly(value)

        return self.from_classical(
            self.attractor,
            self.a,
            self.ecc,
            self.inc,
            self.raan,
            self.argp,
            value,
            epoch=self.epoch + time_of_flight,
            plane=self.plane,
        )