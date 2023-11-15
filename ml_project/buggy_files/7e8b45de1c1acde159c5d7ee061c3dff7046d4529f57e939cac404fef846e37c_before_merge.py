    def setCols(self, headerrows):
        self.columns = []
        for i, colnamelines in enumerate(itertools.zip_longest(*headerrows, fillvalue='')):
            self.addColumn(ColumnItem(''.join(colnamelines), i))

        self._rowtype = namedlist('tsvobj', [(c.name or '_') for c in self.columns])