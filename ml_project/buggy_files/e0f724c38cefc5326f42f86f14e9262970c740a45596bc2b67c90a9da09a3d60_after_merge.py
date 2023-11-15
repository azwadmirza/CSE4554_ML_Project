    def __init__(self, filename, filename_info, filetype_info,
                 engine=None):
        """Init the file handler."""
        super(NCOLCIAngles, self).__init__(filename, filename_info,
                                           filetype_info)
        self.nc = None
        # TODO: get metadata from the manifest file (xfdumanifest.xml)
        self.platform_name = PLATFORM_NAMES[filename_info['mission_id']]
        self.sensor = 'olci'
        self.cache = {}
        self._start_time = filename_info['start_time']
        self._end_time = filename_info['end_time']
        self.engine = engine