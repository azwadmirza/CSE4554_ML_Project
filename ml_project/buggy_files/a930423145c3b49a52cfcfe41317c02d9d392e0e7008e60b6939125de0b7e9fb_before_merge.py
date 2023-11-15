    def openCell(self, col, row):
        k = self.keystr(row) or [str(self.cursorRowIndex)]
        name = f'{self.name}.{col.name}[{self.keystr(row)}]'
        return vd.load_pyobj(name, col.getTypedValue(row))