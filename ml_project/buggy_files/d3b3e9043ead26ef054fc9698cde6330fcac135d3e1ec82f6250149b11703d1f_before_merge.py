    def buffer(self, distance, resolution=16, **kwargs):
        if isinstance(distance, np.ndarray):
            if len(distance) != len(self):
                raise ValueError(
                    "Length of distance sequence does not match "
                    "length of the GeoSeries"
                )
            data = [
                geom.buffer(dist, resolution, **kwargs) if geom is not None else None
                for geom, dist in zip(self.data, distance)
            ]
            return GeometryArray(np.array(data, dtype=object))

        data = [
            geom.buffer(distance, resolution, **kwargs) if geom is not None else None
            for geom in self.data
        ]
        return GeometryArray(np.array(data, dtype=object))