    def iterload(self):
        import openpyxl
        self.workbook = openpyxl.load_workbook(str(self.source), data_only=True, read_only=True)
        for sheetname in self.workbook.sheetnames:
            vs = XlsxSheet(self.name, sheetname, source=self.workbook[sheetname])
            vs.reload()
            yield vs