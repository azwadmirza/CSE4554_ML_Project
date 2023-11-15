    def handle(self):
        """ Callback when we receive any data
        """
        reset_frame = False
        while self.running:
            try:
                data, self.socket = self.request
                if not data:
                    self.running = False
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug('Handling data: ' + hexlify_packets(data))
                # if not self.server.control.ListenOnly:
                units = self.server.context.slaves()
                single = self.server.context.single
                self.framer.processIncomingPacket(data, self.execute,
                                                  units, single=single)
            except socket.timeout: pass
            except socket.error as msg:
                _logger.error("Socket error occurred %s" % msg)
                self.running = False
                reset_frame = True
            except Exception as msg:
                _logger.error(msg)
                self.running = False
                reset_frame = True
            finally:
                # Reset data after processing
                self.request = (None, self.socket)
                if reset_frame:
                    self.framer.resetFrame()
                    reset_frame = False