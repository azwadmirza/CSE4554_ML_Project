    def get_angles(self, angle_id):
        """Get sun-satellite viewing angles"""

        tic = datetime.now()

        sunz40km = self._data["ang"][:, :, 0] * 1e-2
        satz40km = self._data["ang"][:, :, 1] * 1e-2
        azidiff40km = self._data["ang"][:, :, 2] * 1e-2

        try:
            from geotiepoints.interpolator import Interpolator
        except ImportError:
            logger.warning("Could not interpolate sun-sat angles, "
                           "python-geotiepoints missing.")
            self.sunz, self.satz, self.azidiff = sunz40km, satz40km, azidiff40km
        else:
            cols40km = np.arange(24, 2048, 40)
            cols1km = np.arange(2048)
            lines = sunz40km.shape[0]
            rows40km = np.arange(lines)
            rows1km = np.arange(lines)

            along_track_order = 1
            cross_track_order = 3

            satint = Interpolator(
                [sunz40km, satz40km, azidiff40km], (rows40km, cols40km),
                (rows1km, cols1km), along_track_order, cross_track_order)
            self.sunz, self.satz, self.azidiff = satint.interpolate()

            logger.debug("Interpolate sun-sat angles: time %s",
                         str(datetime.now() - tic))

        return Dataset(getattr(self, ANGLES[angle_id]), copy=False)