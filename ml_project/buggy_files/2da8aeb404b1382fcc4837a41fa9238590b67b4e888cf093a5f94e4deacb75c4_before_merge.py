    def toString(self, inObject):
        """
        Convert to send on the wire, with compression.
        """
        return zlib.compress(inObject, 9)