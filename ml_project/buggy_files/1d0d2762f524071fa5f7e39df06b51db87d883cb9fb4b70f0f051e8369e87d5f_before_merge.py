    def __init__(self, filename, filename_info, filetype_info):
        """Initialize FileHandler."""
        super(EPSAVHRRFile, self).__init__(
            filename, filename_info, filetype_info)

        self.lons, self.lats = None, None
        self.sun_azi, self.sun_zen, self.sat_azi, self.sat_zen = None, None, None, None
        self.area = None
        self.three_a_mask, self.three_b_mask = None, None
        self._start_time = filename_info['start_time']
        self._end_time = filename_info['end_time']
        self.records = None
        self.form = None
        self.mdrs = None
        self.scanlines = None
        self.pixels = None
        self.sections = None