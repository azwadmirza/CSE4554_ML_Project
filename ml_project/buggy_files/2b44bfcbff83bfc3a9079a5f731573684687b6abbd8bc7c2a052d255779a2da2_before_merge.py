    def __init__(self, filename, filename_info, filetype_info):
        super(NCOLCI1B, self).__init__(filename, filename_info,
                                       filetype_info)
        self.nc = h5netcdf.File(filename, 'r')
        self.channel = filename_info['dataset_name']
        cal_file = os.path.join(os.path.dirname(
            filename), 'instrument_data.nc')
        self.cal = h5netcdf.File(cal_file, 'r')
        # TODO: get metadata from the manifest file (xfdumanifest.xml)
        self.platform_name = PLATFORM_NAMES[filename_info['mission_id']]
        self.sensor = 'olci'