    def _sample_open(self, values, min_anomaly, max_anomaly):
        # Select a sensible limiting value for non-closed orbits
        # This corresponds to max(r = 3p, r = self.r)
        # We have to wrap nu in [-180, 180) to compare it with the output of
        # the arc cosine, which is in the range [0, 180)
        # Start from -nu_limit
        wrapped_nu = Angle(self.nu).wrap_at(180 * u.deg)
        nu_limit = max(hyp_nu_limit(self.ecc, 3.0), abs(wrapped_nu)).to(u.rad).value

        limits = [
            min_anomaly.to(u.rad).value if min_anomaly is not None else -nu_limit,
            max_anomaly.to(u.rad).value if max_anomaly is not None else nu_limit,
        ] * u.rad  # type: u.Quantity

        # Now we check that none of the provided values
        # is outside of the hyperbolic range
        nu_max = hyp_nu_limit(self.ecc) - 1e-3 * u.rad  # Arbitrary delta
        if not Angle(limits).is_within_bounds(-nu_max, nu_max):
            warn("anomaly outside range, clipping", OrbitSamplingWarning, stacklevel=2)
            limits = limits.clip(-nu_max, nu_max)

        nu_values = np.linspace(*limits, values)  # type: ignore
        return nu_values