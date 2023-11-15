    def datagram_received(self, data, _):
        """DNS response packet received."""
        log_binary(_LOGGER, "Received DNS response from " + str(self.host), Data=data)

        self.result = DnsMessage().unpack(data)
        self.transport.close()
        self._finished()