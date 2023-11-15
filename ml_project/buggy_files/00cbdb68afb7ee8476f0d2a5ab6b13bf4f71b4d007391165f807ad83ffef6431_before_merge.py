    def get_dataset(self, key, info):
        """Get a dataset from the file."""

        if key.name in CHANNEL_NAMES:
            dataset = self.calibrate([key])[0]
            # dataset.info.update(info)
        elif key.name in ['longitude', 'latitude']:
            if self.lons is None or self.lats is None:
                self.navigate()
            if key.name == 'longitude':
                return Dataset(self.lons, id=key, **info)
            else:
                return Dataset(self.lats, id=key, **info)
        else:  # Get sun-sat angles
            if key.name in ANGLES:
                if isinstance(getattr(self, ANGLES[key.name]), np.ndarray):
                    dataset = Dataset(
                        getattr(self, ANGLES[key.name]),
                        copy=False)
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