    def openRow(self, row):
        k = self.rowkey(row) or [self.cursorRowIndex]
        name = f'{self.name}[{k}]'
        return vd.load_pyobj(name, tuple(c.getTypedValue(row) for c in self.visibleCols))