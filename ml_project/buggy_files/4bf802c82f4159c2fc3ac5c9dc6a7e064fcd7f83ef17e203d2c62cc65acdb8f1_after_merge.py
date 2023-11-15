    def fromString(self, inString):
        """
        Convert (decompress) from the string-representation on the wire to Python.
        """
        return super(Compressed, self).fromString(zlib.decompress(inString))