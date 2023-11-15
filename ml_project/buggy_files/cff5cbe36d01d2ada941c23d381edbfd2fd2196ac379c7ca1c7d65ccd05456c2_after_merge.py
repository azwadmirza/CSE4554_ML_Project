    def handle(self):
        """ Callback when we receive any data
        """
        while self.running:
            try:
                data = self.request.recv(1024)
                if data:
                    units = self.server.context.slaves()
                    if not isinstance(units, (list, tuple)):
                        units = [units]
                    # if broadcast is enabled make sure to process requests to address 0
                    if self.server.broadcast_enable:
                        if 0 not in units:
                            units.append(0)
                    single = self.server.context.single
                    self.framer.processIncomingPacket(data, self.execute,
                                                      units, single=single)
            except Exception as msg:
                # Since we only have a single socket, we cannot exit
                # Clear frame buffer
                self.framer.resetFrame()
                _logger.debug("Error: Socket error occurred %s" % msg)