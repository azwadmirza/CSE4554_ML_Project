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
            if raw:
                projectables.append(data)
            else:
                projectables.append(Dataset(data, id=key))

        return projectables