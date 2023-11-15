    def get(self):
        self.session.logging.info(f'Get packet: {self.__class__.__name__}')

        len_header = MAX_PACKET_SIZE
        body = b''
        count_header = 1
        while len_header == MAX_PACKET_SIZE:
            packet_string = self.mysql_socket.recv(4)
            if len(packet_string) < 4:
                self.session.logging.warning(f'Packet with less than 4 bytes in length: {packet_string}')
                return False
                break
            len_header = struct.unpack('i', packet_string[:3] + b'\x00')[0]
            count_header = int(packet_string[3])
            if len_header == 0:
                break
            body += self.mysql_socket.recv(len_header)
        self.session.logging.info(f'Got packet: {str(body)}')
        self.proxy.count = int(count_header) + 1
        self.setup(len(body), count_header, body)
        return True