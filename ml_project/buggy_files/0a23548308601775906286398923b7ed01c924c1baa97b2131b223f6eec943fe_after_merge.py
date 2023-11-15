    def __init__(self) -> None:
        self.first_attempt = True
        self.decompressor = zlib.decompressobj()