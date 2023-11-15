    def __init__(self, ds, io, filename, file_id):
        gformat = _get_gadget_format(filename, ds._header_size)
        with open(filename, "rb") as f:
            if gformat[0] == 2:
                f.seek(f.tell() + SNAP_FORMAT_2_OFFSET)
            self.header = read_record(f, ds._header_spec, endian=gformat[1])
            if gformat[0] == 2:
                f.seek(f.tell() + SNAP_FORMAT_2_OFFSET)
            self._position_offset = f.tell()
            f.seek(0, os.SEEK_END)
            self._file_size = f.tell()

        super(GadgetBinaryFile, self).__init__(ds, io, filename, file_id)