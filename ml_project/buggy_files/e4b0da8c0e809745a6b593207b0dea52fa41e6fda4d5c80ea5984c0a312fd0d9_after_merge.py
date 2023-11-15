    def interpolate(self, distance, normalized=False):
        data = data = np.empty(len(self), dtype=object)
        if isinstance(distance, np.ndarray):
            if len(distance) != len(self):
                raise ValueError(
                    "Length of distance sequence does not match "
                    "length of the GeoSeries"
                )
            data[:] = [
                geom.interpolate(dist, normalized=normalized)
                for geom, dist in zip(self.data, distance)
            ]
            return GeometryArray(data)

        data[:] = [
            geom.interpolate(distance, normalized=normalized) for geom in self.data
        ]
        return GeometryArray(data)