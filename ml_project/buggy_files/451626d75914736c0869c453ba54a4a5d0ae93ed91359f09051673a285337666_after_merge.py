    def reload(self):
        # key rows become column names
        col = Column('_'.join(c.name for c in self.source.keyCols),
                getter=lambda c,origcol: origcol.name)
        # associate column with sheet
        col.recalc(self)
        self.columns = [col]
        self.setKeys(self.columns)


        # rows become columns
        for row in Progress(self.source.rows, 'transposing'):
            self.addColumn(Column('_'.join(map(str, self.source.rowkey(row))),
                                  getter=lambda c,origcol,row=row: origcol.getValue(row)))

        # columns become rows
        self.rows = list(self.source.nonKeyVisibleCols)