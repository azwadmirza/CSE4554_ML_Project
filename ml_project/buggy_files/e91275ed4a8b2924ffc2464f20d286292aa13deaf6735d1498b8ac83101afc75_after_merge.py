    def convert_input(self, value):
        # Keep string here.
        if isinstance(value, str):
            return value, False
        else:
            # Upgrade the coordinate to a `SkyCoord` so that frame attributes will be merged
            if isinstance(value, BaseCoordinateFrame) and not isinstance(value, self._frame):
                value = SkyCoord(value)

            return super().convert_input(value)