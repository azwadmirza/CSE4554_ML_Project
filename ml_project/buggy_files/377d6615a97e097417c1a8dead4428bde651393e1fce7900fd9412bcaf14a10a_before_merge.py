    def packet(self, packetClass=Packet, **kwargs):
        """
        Factory method for packets

        :param packetClass:
        :param kwargs:
        :return:
        """
        p = packetClass(socket=self.socket, seq=self.count, session=self.session, proxy=self, **kwargs)
        self.count += 1
        return p