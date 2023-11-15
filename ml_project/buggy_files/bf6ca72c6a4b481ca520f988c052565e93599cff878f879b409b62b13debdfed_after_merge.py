    def get_angles(self, angle_id):
        """Get sun-satellite viewing angles."""
        sunz, satz, azidiff = self._get_all_interpolated_angles()

        name_to_variable = dict(zip(ANGLES, (satz, sunz, azidiff)))
        return create_xarray(name_to_variable[angle_id])