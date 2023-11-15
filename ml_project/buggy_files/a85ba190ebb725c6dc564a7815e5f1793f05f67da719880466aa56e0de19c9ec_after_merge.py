    def getPacketString(self):
        body = self.body
        len_header = struct.pack('<i', self.length)[:3]  # keep it 3 bytes
        count_header = struct.pack('B', self.seq)
        packet = len_header + count_header + body
        return packet