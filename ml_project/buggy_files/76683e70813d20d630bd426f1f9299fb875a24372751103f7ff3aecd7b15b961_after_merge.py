    def __init__(self, filename, instrument=None):
        SFS_reader.__init__(self, filename)
        header_file = self.get_file('EDSDatabase/HeaderData')
        self.available_indexes = []
        for i in self.vfs['EDSDatabase'].keys():
            if 'SpectrumData' in i:
                self.available_indexes.append(int(i[-1]))
        self.def_index = min(self.available_indexes)
        header_byte_str = header_file.get_as_BytesIO_string().getvalue()
        self.header = HyperHeader(header_byte_str, self.available_indexes, instrument=instrument)
        self.hypermap = {}