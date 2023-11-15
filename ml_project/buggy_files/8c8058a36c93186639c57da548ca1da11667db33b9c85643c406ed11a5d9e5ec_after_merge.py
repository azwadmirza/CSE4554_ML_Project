    def load(self, keys, interpolate=True, raw=False):
        """Load the data."""
        projectables = []
        for key in keys:
            dataset = self.sd.select(key.name.capitalize())
            fill_value = dataset.attributes()["_FillValue"]
            try:
                scale_factor = dataset.attributes()["scale_factor"]
            except KeyError:
                scale_factor = 1
            data = np.ma.masked_equal(dataset.get(), fill_value) * scale_factor

            # TODO: interpolate if needed
            if (key.resolution is not None and
                    key.resolution < self.resolution and
                    interpolate):
                data = self._interpolate(data, self.resolution, key.resolution)
            if not raw:
                data = data.filled(np.nan)
                data = xr.DataArray(da.from_array(data, chunks=(CHUNK_SIZE,
                                                                CHUNK_SIZE)),
                                    dims=['y', 'x'])
            projectables.append(data)

        return projectables