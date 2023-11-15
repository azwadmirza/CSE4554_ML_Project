    def __init__(self, filename, filename_info, filetype_info):
        """Initialize object information by reading the input file."""
        super(AVHRRAAPPL1BFile, self).__init__(filename, filename_info,
                                               filetype_info)
        self.channels = {i: None for i in AVHRR_CHANNEL_NAMES}
        self.units = {i: 'counts' for i in AVHRR_CHANNEL_NAMES}

        self._data = None
        self._header = None
        self._is3b = None
        self._is3a = None
        self._shape = None
        self.area = None
        self.sensor = 'avhrr-3'
        self.read()

        self.active_channels = self._get_active_channels()

        self.platform_name = PLATFORM_NAMES.get(self._header['satid'][0], None)

        if self.platform_name is None:
            raise ValueError("Unsupported platform ID: %d" % self.header['satid'])