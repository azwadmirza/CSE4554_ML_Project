    def openRow(self, row):
        return load_pyobj("%s[%s]" % (self.name, self.keystr(row)), row)