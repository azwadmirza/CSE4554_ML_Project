    def fromString(self, inString):
        """
        Convert (decompress) from the wire to Python.
        """
        return zlib.decompress(inString)