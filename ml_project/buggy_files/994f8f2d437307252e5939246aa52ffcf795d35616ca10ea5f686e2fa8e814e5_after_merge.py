    def parse(self, file):
        file = EncodedIO(file)
        file = io.TextIOWrapper(file, encoding=file.encoding)
        reader = csv.reader(file)
        yield from ExcelParser.parse_excel_csv_reader(reader)