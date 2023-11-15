    def __init__(self) -> None:
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)