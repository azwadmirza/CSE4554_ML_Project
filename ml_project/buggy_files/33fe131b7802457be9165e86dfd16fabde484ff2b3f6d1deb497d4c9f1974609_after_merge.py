    def _generate_items(self, df, columns):
        """Produce list of unique tuples that identify each item."""
        if not self.bin:
            super(ColorAttr, self)._generate_items(df, columns)
        else:

            if len(columns) == 1 and ChartDataSource.is_number(df[columns[0]]):

                self.bins = Bins(source=ColumnDataSource(df), column=columns[0],
                                 bin_count=len(self.iterable), aggregate=False)

                if self.sort:
                    self.bins.sort(ascending=self.ascending)

                self.items = [bin.label[0] for bin in self.bins]
            else:
                raise ValueError('Binned colors can only be created for one column of \
                                 numerical data.')