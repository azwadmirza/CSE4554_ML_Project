    def get_dataset(self, key, info):

        if self.reader is None:

            with open(self.filename) as fdes:
                data = fdes.read(3)
            if data in ["CMS", "NSS", "UKM", "DSS"]:
                reader = GACKLMReader
                self.chn_dict = AVHRR3_CHANNEL_NAMES
            else:
                reader = GACPODReader
                self.chn_dict = AVHRR_CHANNEL_NAMES

            self.reader = reader()
            self.reader.read(self.filename)

        if key.name in ['latitude', 'longitude']:
            if self.reader.lons is None or self.reader.lats is None:
                self.reader.get_lonlat(clock_drift_adjust=False)
            if key.name == 'latitude':
                return Dataset(self.reader.lats, id=key, **info)
            else:
                return Dataset(self.reader.lons, id=key, **info)

        if self.channels is None:
            self.channels = self.reader.get_calibrated_channels()

        data = self.channels[:, :, self.chn_dict[key.name]]
        return Dataset(data, id=key, **info)