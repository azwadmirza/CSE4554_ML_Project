    def __init__(self, filename, filename_info, filetype_info):
        """Init the olci reader base."""
        super(NCOLCIBase, self).__init__(filename, filename_info,
                                         filetype_info)
        self.nc = xr.open_dataset(self.filename,
                                  decode_cf=True,
                                  mask_and_scale=True,
                                  engine='h5netcdf',
                                  chunks={'columns': CHUNK_SIZE,
                                          'rows': CHUNK_SIZE})

        self.nc = self.nc.rename({'columns': 'x', 'rows': 'y'})

        # TODO: get metadata from the manifest file (xfdumanifest.xml)
        self.platform_name = PLATFORM_NAMES[filename_info['mission_id']]
        self.sensor = 'olci'