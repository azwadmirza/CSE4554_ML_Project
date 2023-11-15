    def __init__(self, filename, filename_info, filetype_info):
        """Init method"""
        super(NcNWCSAF, self).__init__(filename, filename_info,
                                       filetype_info)
        self.nc = h5netcdf.File(filename, 'r')
        self.pps = False

        try:
            # MSG:
            sat_id = self.nc.attrs['satellite_identifier']
            self.platform_name = PLATFORM_NAMES[sat_id]
        except KeyError:
            # PPS:
            self.platform_name = self.nc.attrs['platform']
            self.pps = True

        self.sensor = SENSOR.get(self.platform_name, 'seviri')