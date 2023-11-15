    def get_dataset(self, key, info):
        """Get a dataset from the file."""

        if key.name in CHANNEL_NAMES:
            dataset = self.calibrate([key])[0]
        elif key.name in ['longitude', 'latitude']:
            if self.lons is None or self.lats is None:
                self.navigate()
            if key.name == 'longitude':
                dataset = create_xarray(self.lons)
            else:
                dataset = create_xarray(self.lats)
            dataset.attrs = info
        else:  # Get sun-sat angles
            if key.name in ANGLES:
                if isinstance(getattr(self, ANGLES[key.name]), np.ndarray):
                    dataset = getattr(self, ANGLES[key.name])
                else:
                    dataset = self.get_angles(key.name)
            else:
                logger.exception(
                    "Not a supported sun-sensor viewing angle: %s", key.name)
                raise

        # TODO get metadata

        if not self._shape:
            self._shape = dataset.shape

        return dataset