    def _get_header(self):
        """Read the header info"""

        hdrrec = Msg15NativeHeaderRecord().get()
        hd_dt = np.dtype(hdrrec)
        hd_dt = hd_dt.newbyteorder('>')
        self.header = np.fromfile(self.filename, dtype=hd_dt, count=1)

        # Set the list of available channels:
        chlist_str = self.header['15_SECONDARY_PRODUCT_HEADER'][
            'SelectedBandIDs'][0][-1].strip()
        for item, chmark in zip(CHANNEL_LIST, chlist_str):
            self.available_channels[item] = (chmark == 'X')

        self.platform_id = self.header['15_DATA_HEADER'][
            'SatelliteStatus']['SatelliteDefinition']['SatelliteId'][0]
        self.platform_name = "Meteosat-" + SATNUM[self.platform_id]

        ssp_lon = self.header['15_DATA_HEADER']['ImageDescription'][
            'ProjectionDescription']['LongitudeOfSSP'][0]

        self.mda = {}
        equator_radius = self.header['15_DATA_HEADER']['GeometricProcessing'][
            'EarthModel']['EquatorialRadius'][0] * 1000.
        north_polar_radius = self.header['15_DATA_HEADER'][
            'GeometricProcessing']['EarthModel']['NorthPolarRadius'][0] * 1000.
        south_polar_radius = self.header['15_DATA_HEADER'][
            'GeometricProcessing']['EarthModel']['SouthPolarRadius'][0] * 1000.
        polar_radius = (north_polar_radius + south_polar_radius) * 0.5
        self.mda['projection_parameters'] = {'a': equator_radius,
                                             'b': polar_radius,
                                             'h': 35785831.00,
                                             'SSP_longitude': ssp_lon}
        self.mda['number_of_lines'] = self.header['15_DATA_HEADER'][
            'ImageDescription']['ReferenceGridVIS_IR']['NumberOfLines'][0]
        self.mda['number_of_columns'] = self.header['15_DATA_HEADER'][
            'ImageDescription']['ReferenceGridVIS_IR']['NumberOfColumns'][0]

        sec15hd = self.header['15_SECONDARY_PRODUCT_HEADER']
        numlines_visir = int(sec15hd['NumberLinesVISIR']['Value'][0])
        west = int(sec15hd['WestColumnSelectedRectangle']['Value'][0])
        east = int(sec15hd['EastColumnSelectedRectangle']['Value'][0])
        north = int(sec15hd["NorthLineSelectedRectangle"]['Value'][0])
        south = int(sec15hd["SouthLineSelectedRectangle"]['Value'][0])
        numcols_hrv = int(sec15hd["NumberColumnsHRV"]['Value'][0])

        # Subsetting doesn't work unless number of pixels on a line
        # divded by 4 is a whole number!
        # FIXME!
        if abs(int(numlines_visir / 4.) - numlines_visir / 4.) > 0.001:
            msgstr = (
                "Number of pixels in east-west direction needs to be a multiple of 4!" +
                "\nPlease get the full disk!")
            raise NotImplementedError(msgstr)

        # Data are stored in 10 bits!
        self._cols_visir = int(np.ceil(numlines_visir * 10.0 / 8))  # 4640
        if (west - east) < 3711:
            self._cols_hrv = int(np.ceil(numcols_hrv * 10.0 / 8))  # 6960
        else:
            self._cols_hrv = int(np.ceil(5568 * 10.0 / 8))  # 6960

        #'WestColumnSelectedRectangle' - 'EastColumnSelectedRectangle'
        #'NorthLineSelectedRectangle' - 'SouthLineSelectedRectangle'

        coldir_step = self.header['15_DATA_HEADER']['ImageDescription'][
            "ReferenceGridVIS_IR"]["ColumnDirGridStep"][0] * 1000.0
        lindir_step = self.header['15_DATA_HEADER']['ImageDescription'][
            "ReferenceGridVIS_IR"]["LineDirGridStep"][0] * 1000.0
        area_extent = ((1856 - west - 0.5) * coldir_step,
                       (1856 - north + 0.5) * lindir_step,
                       (1856 - east + 0.5) * coldir_step,
                       (1856 - south + 1.5) * lindir_step)

        self.area_extent = area_extent

        self.data_len = numlines_visir