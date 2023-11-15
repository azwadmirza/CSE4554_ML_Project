    def __init__(self, path, engine=None, encoding=None, **engine_kwargs):
        # Use the xlwt module as the Excel writer.
        import xlwt

        super(_XlwtWriter, self).__init__(path, **engine_kwargs)

        if encoding is None:
            encoding = 'ascii'
        self.book = xlwt.Workbook(encoding=encoding)
        self.fm_datetime = xlwt.easyxf(num_format_str=self.datetime_format)
        self.fm_date = xlwt.easyxf(num_format_str=self.date_format)