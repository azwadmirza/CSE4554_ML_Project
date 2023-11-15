    def _read_trz_header(self):
        """Reads the header of the trz trajectory"""
        self._headerdtype = np.dtype([
            ('p1', '<i4'),
            ('title', '80c'),
            ('p2', '<2i4'),
            ('force', '<i4'),
            ('p3', '<i4')])
        data = np.fromfile(self.trzfile, dtype=self._headerdtype, count=1)
        self.title = ''.join(c.decode('utf-8') for c in data['title'][0]).strip()
        if data['force'] == 10:
            self.has_force = False
        elif data['force'] == 20:
            self.has_force = True
        else:
            raise IOError