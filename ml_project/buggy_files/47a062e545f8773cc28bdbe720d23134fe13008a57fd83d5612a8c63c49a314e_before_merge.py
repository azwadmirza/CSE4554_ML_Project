    def propagate(self, value, method=mean_motion, rtol=1e-10, **kwargs):
        """Propagates an orbit a specified time.

        If value is true anomaly, propagate orbit to this anomaly and return the result.
        Otherwise, if time is provided, propagate this `Orbit` some `time` and return the result.

        Parameters
        ----------
        value : ~astropy.units.Quantity, ~astropy.time.Time, ~astropy.time.TimeDelta
            Scalar time to propagate.
        rtol : float, optional
            Relative tolerance for the propagation algorithm, default to 1e-10.
        method : function, optional
            Method used for propagation
        **kwargs
            parameters used in perturbation models

        Returns
        -------
        Orbit
            New orbit after propagation.

        """
        if isinstance(value, time.Time) and not isinstance(value, time.TimeDelta):
            time_of_flight = value - self.epoch
        else:
            # Works for both Quantity and TimeDelta objects
            time_of_flight = time.TimeDelta(value)

        cartesian = propagate(self, time_of_flight, method=method, rtol=rtol, **kwargs)

        # If the frame supports obstime, set the time values
        kwargs = {}
        if "obstime" in self.frame.frame_attributes:
            kwargs["obstime"] = self.epoch + time_of_flight
        else:
            warn(
                "Frame {} does not support 'obstime', time values were not returned".format(
                    self.frame.__class__
                )
            )

        # Use of a protected method instead of frame.realize_frame
        # because the latter does not let the user choose the representation type
        # in one line despite its parameter names, see
        # https://github.com/astropy/astropy/issues/7784
        coords = self.frame._replicate(
            cartesian, representation_type="cartesian", **kwargs
        )

        return self.from_coords(self.attractor, coords, plane=self.plane)