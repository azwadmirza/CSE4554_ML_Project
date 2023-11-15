    def _read_all(self, filename):
        LOG.debug("Reading %s", filename)
        self.records, self.form = read_raw(filename)
        self.mdrs = [record
                     for record in self.records
                     if record_class[record['record_class']] == "mdr"]
        self.iprs = [record
                     for record in self.records
                     if record_class[record['record_class']] == "ipr"]
        self.scanlines = len(self.mdrs)
        self.sections = {("mdr", 2): np.hstack(self.mdrs)}
        self.sections[("ipr", 0)] = np.hstack(self.iprs)
        for record in self.records:
            rec_class = record_class[record['record_class']]
            sub_class = record["RECORD_SUBCLASS"]
            if rec_class in ["mdr", "ipr"]:
                continue
            if (rec_class, sub_class) in self.sections:
                raise ValueError("Too many " + str((rec_class, sub_class)))
            else:
                self.sections[(rec_class, sub_class)] = record
        self.pixels = self["EARTH_VIEWS_PER_SCANLINE"]