    def loadFromPacketString(self, packet_string):
        len_header = struct.unpack('>i', struct.pack('1s', '') + packet_string[:3])[0]
        count_header = struct.unpack('b', packet_string[3])[0]
        body = packet_string[4:]
        self.loadFromParams(length=len_header, seq=count_header, body=body)