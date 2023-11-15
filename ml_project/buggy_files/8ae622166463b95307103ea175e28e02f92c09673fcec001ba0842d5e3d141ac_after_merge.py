    def __init__(self, ds, io, filename, file_id):
        header = ds._header
        self.header = header.value
        self._position_offset = header.position_offset
        with header.open() as f:
            self._file_size = f.seek(0, os.SEEK_END)

        super(GadgetBinaryFile, self).__init__(ds, io, filename, file_id)