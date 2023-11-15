        def callback(*args):
            LOGGER.debug("in callback - {}".format(request.transaction_id))
            while True:
                waiting = self.stream.connection.in_waiting
                if waiting:
                    data = self.stream.connection.read(waiting)
                    LOGGER.debug(
                        "recv: " + " ".join([hex(byte2int(x)) for x in data]))
                    self.framer.processIncomingPacket(
                        data,
                        self._handle_response,
                        tid=request.transaction_id
                    )
                    break