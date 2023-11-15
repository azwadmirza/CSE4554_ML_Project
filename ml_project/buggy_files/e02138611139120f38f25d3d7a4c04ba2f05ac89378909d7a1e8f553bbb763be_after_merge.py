    def execute(self, request=None):
        """
        Executes a transaction
        :param request: Request to be written on to the bus
        :return:
        """
        request.transaction_id = self.transaction.getNextTID()

        def callback(*args):
            LOGGER.debug("in callback - {}".format(request.transaction_id))
            while True:
                waiting = self.stream.connection.in_waiting
                if waiting:
                    data = self.stream.connection.read(waiting)
                    LOGGER.debug(
                        "recv: " + " ".join([hex(byte2int(x)) for x in data]))
                    unit = self.framer.decode_data(data).get("uid", 0)
                    self.framer.processIncomingPacket(
                        data,
                        self._handle_response,
                        unit,
                        tid=request.transaction_id
                    )
                    break

        packet = self.framer.buildPacket(request)
        LOGGER.debug("send: " + " ".join([hex(byte2int(x)) for x in packet]))
        self.stream.write(packet, callback=callback)
        f = self._build_response(request.transaction_id)
        return f