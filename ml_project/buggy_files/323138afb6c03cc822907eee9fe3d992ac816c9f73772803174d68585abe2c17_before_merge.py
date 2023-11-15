    def openRow(self, row):
        k = self.rowkey(row) or [self.cursorRowIndex]
        name = f'{self.name}[{self.keystr(row)}]'
        return vd.load_pyobj(tuple(c.getTypedValue(row) for c in self.visibleCols))