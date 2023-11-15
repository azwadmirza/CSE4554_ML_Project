    def __init__(self, filename, filename_info, filetype_info, cal):
        super(NCOLCI1B, self).__init__(filename, filename_info,
                                         filetype_info)
        self.cal = cal.nc