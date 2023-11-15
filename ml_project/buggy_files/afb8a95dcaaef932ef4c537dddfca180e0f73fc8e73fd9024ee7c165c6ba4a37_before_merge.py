    def checkFrame(self):
        """
        Check if the next frame is available.
        Return True if we were successful.

        1. Populate header
        2. Discard frame if UID does not match
        """
        try:
            self.populateHeader()
            frame_size = self._header['len']
            data = self._buffer[:frame_size - 2]
            crc = self._buffer[frame_size - 2:frame_size]
            crc_val = (byte2int(crc[0]) << 8) + byte2int(crc[1])
            return checkCRC(data, crc_val)
        except (IndexError, KeyError, struct.error):
            return False