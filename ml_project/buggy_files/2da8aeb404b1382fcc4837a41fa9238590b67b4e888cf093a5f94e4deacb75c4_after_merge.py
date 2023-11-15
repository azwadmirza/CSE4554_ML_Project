    def toString(self, inObject):
        """
        Convert to send as a string on the wire, with compression.
        """
        return zlib.compress(super(Compressed, self).toString(inObject), 9)