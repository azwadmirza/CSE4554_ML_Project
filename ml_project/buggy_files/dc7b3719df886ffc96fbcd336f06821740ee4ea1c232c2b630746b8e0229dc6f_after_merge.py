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
        # Silently wrap anomaly
        nu = (value + np.pi * u.rad) % (2 * np.pi * u.rad) - np.pi * u.rad

        # Compute time of flight for correct epoch
        time_of_flight = self.time_to_anomaly(nu)

        if time_of_flight < 0:
            if self.ecc >= 1:
                raise ValueError("True anomaly {:.2f} not reachable".format(value))
            else:
                # For a closed orbit, instead of moving backwards
                # we need to do another revolution
                time_of_flight = self.period - time_of_flight

        return self.from_classical(
            self.attractor,
            self.a,
            self.ecc,
            self.inc,
            self.raan,
            self.argp,
            nu,
            epoch=self.epoch + time_of_flight,
            plane=self.plane,
        )