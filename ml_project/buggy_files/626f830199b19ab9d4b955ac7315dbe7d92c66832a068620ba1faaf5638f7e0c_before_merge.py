    def _vis_calibrate(self, data):
        """Calibrate visible channels to reflectance."""
        solar_irradiance = self.nc['esun'][()]
        esd = self.nc["earth_sun_distance_anomaly_in_AU"][()]

        factor = np.pi * esd * esd / solar_irradiance
        data.data[:] *= factor

        return '1'