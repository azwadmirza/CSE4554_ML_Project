    def openCell(self, col, row):
        k = self.keystr(row) or [str(self.cursorRowIndex)]
        name = f'{self.name}.{col.name}[{k}]'
        return vd.load_pyobj(name, col.getTypedValue(row))