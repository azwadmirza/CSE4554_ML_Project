    def iterload(self):
        import openpyxl
        self.workbook = openpyxl.load_workbook(str(self.source), data_only=True, read_only=True)
        for sheetname in self.workbook.sheetnames:
            src = self.workbook[sheetname]
            vs = XlsxSheet(self.name, sheetname, source=src)
            if isinstance(src, openpyxl.Workbook):
                vs.reload()
            yield vs