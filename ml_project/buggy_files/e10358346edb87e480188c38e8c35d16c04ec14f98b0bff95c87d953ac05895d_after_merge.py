    def _read_all(self):
        logger.debug("Reading %s", self.filename)
        self.sections, self.form = read_records(self.filename)
        self.scanlines = self['TOTAL_MDR']
        if self.scanlines != len(self.sections[('mdr', 2)]):
            logger.warning("Number of declared records doesn't match number of scanlines in the file.")
        self.pixels = self["EARTH_VIEWS_PER_SCANLINE"]