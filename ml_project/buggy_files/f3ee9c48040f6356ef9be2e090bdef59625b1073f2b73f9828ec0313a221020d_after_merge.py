    def __init__(self, filename):
        self.fp = open(filename, "rb")
        data = self.fp.read(FILE_HEADER_STRUCT.size)
        header = FILE_HEADER_STRUCT.unpack(data)
        #print(header)
        if header[0] != b"LOGG":
            raise BLFParseError("Unexpected file format")
        self.file_size = header[10]
        self.uncompressed_size = header[11]
        self.object_count = header[12]
        self.start_timestamp = systemtime_to_timestamp(header[14:22])
        self.stop_timestamp = systemtime_to_timestamp(header[22:30])
        # Read rest of header
        self.fp.read(header[1] - FILE_HEADER_STRUCT.size)