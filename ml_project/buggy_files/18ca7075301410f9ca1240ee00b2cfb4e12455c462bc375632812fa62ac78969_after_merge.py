    def calc_area_extent(self, key):
        """Calculate area extent for a dataset.
        """
        # Calculate the area extent of the swath based on start line and column
        # information, total number of segments and channel resolution
        xyres = {500: 22272, 1000: 11136, 2000: 5568}
        chkres = xyres[key.resolution]

        # Get metadata for given dataset
        measured = self.nc['/data/{}/measured'.format(key.name)]
        variable = self.nc['/data/{}/measured/effective_radiance'
                           .format(key.name)]
        # Get start/end line and column of loaded swath.
        self.startline = int(measured['start_position_row'][...])
        self.endline = int(measured['end_position_row'][...])
        self.startcol = int(measured['start_position_column'][...])
        self.endcol = int(measured['end_position_column'][...])
        self.nlines, self.ncols = variable[:].shape

        logger.debug('Channel {} resolution: {}'.format(key.name, chkres))
        logger.debug('Row/Cols: {} / {}'.format(self.nlines, self.ncols))
        logger.debug('Start/End row: {} / {}'.format(self.startline,
                                                     self.endline))
        logger.debug('Start/End col: {} / {}'.format(self.startcol,
                                                     self.endcol))
        total_segments = 70

        # Calculate full globe line extent
        max_y = 5432229.9317116784
        min_y = -5429229.5285458621
        full_y = max_y + abs(min_y)
        # Single swath line extent
        res_y = full_y / chkres  # Extent per pixel resolution
        startl = min_y + res_y * self.startline - 0.5 * (res_y)
        endl = min_y + res_y * self.endline + 0.5 * (res_y)
        logger.debug('Start / end extent: {} / {}'.format(startl, endl))

        chk_extent = (-5432229.9317116784, endl,
                      5429229.5285458621, startl)
        return(chk_extent)