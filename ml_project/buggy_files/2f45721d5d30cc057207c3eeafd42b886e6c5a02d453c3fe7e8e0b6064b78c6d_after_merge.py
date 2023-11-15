    def get_dataset(self, key, info):
        """Get a dataset from the file."""
        if key['name'] in CHANNEL_NAMES:
            if self.active_channels[key['name']]:
                dataset = self.calibrate(key)
            else:
                return None
        elif key['name'] in ['longitude', 'latitude']:
            dataset = self.navigate(key['name'])
            dataset.attrs = info
        elif key['name'] in ANGLES:
            dataset = self.get_angles(key['name'])
        else:
            raise ValueError("Not a supported dataset: %s", key['name'])

        self._update_dataset_attributes(dataset, key, info)

        if not self._shape:
            self._shape = dataset.shape

        return dataset