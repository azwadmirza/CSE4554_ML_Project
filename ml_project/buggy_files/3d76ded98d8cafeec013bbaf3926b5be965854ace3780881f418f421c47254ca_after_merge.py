    def on_receive(self, *args):
        """
        On data recieve call back
        :param args: data received
        :return:
        """
        data = args[0] if len(args) > 0 else None

        if not data:
            return
        LOGGER.debug("recv: " + " ".join([hex(byte2int(x)) for x in data]))
        unit = self.framer.decode_data(data).get("unit", 0)
        self.framer.processIncomingPacket(data, self._handle_response, unit=unit)