    def _writeheader(self, title):
        hdt = np.dtype([
            ('pad1', 'i4'), ('title', '80c'), ('pad2', 'i4'),
            ('pad3', 'i4'), ('nrec', 'i4'), ('pad4', 'i4')])
        out = np.zeros((), dtype=hdt)
        out['pad1'], out['pad2'] = 80, 80
        out['title'] = title + ' ' * (80 - len(title))
        out['pad3'], out['pad4'] = 4, 4
        out['nrec'] = 10
        out.tofile(self.trzfile)