    def __init__(self, filename, filename_info, filetype_info):
        """Init method."""
        super(NcNWCSAF, self).__init__(filename, filename_info,
                                       filetype_info)
        self.nc = xr.open_dataset(filename,
                                  decode_cf=True,
                                  mask_and_scale=False,
                                  engine='h5netcdf',
                                  chunks=1000)

        self.nc = self.nc.rename({'nx': 'x', 'ny': 'y'})

        self.pps = False

        try:
            # MSG:
            sat_id = self.nc.attrs['satellite_identifier']
            try:
                self.platform_name = PLATFORM_NAMES[sat_id]
            except KeyError:
                self.platform_name = PLATFORM_NAMES[sat_id.astype(str)]
        except KeyError:
            # PPS:
            self.platform_name = self.nc.attrs['platform']
            self.pps = True

        self.sensor = SENSOR.get(self.platform_name, 'seviri')