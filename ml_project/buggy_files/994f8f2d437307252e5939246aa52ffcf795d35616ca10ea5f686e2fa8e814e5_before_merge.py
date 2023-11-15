    def parse(self, file):
        file = io.TextIOWrapper(file, encoding='utf-8')
        reader = csv.reader(file)
        yield from ExcelParser.parse_excel_csv_reader(reader)