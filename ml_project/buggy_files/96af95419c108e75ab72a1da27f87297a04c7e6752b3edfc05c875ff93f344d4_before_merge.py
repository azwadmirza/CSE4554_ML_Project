    def __init__(self, f: BinaryIO, encoding: str):
        self.reader = codecs.getreader(encoding)(f)