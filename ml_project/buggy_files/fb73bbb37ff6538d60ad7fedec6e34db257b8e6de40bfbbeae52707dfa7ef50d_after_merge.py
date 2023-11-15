    def __init__(self, filename, channel=1):
        self.fp = open(filename, "wb")
        self.channel = channel
        # Header will be written after log is done
        self.fp.write(b"\x00" * FILE_HEADER_SIZE)
        self.cache = []
        self.cache_size = 0
        self.count_of_objects = 0
        self.uncompressed_size = FILE_HEADER_SIZE
        self.start_timestamp = None
        self.stop_timestamp = None