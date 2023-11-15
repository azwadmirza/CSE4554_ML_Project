    def _transact(self, packet, response_length, full=False):
        """
        Does a Write and Read transaction
        :param packet: packet to be sent
        :param response_length:  Expected response length
        :param full: the target device was notorious for its no response. Dont
            waste time this time by partial querying
        :return: response
        """
        last_exception = None
        try:
            self.client.connect()
            packet = self.client.framer.buildPacket(packet)
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("SEND: " + hexlify_packets(packet))
            size = self._send(packet)
            if size:
                _logger.debug("Changing transaction state from 'SENDING' "
                              "to 'WAITING FOR REPLY'")
                self.client.state = ModbusTransactionState.WAITING_FOR_REPLY
            result = self._recv(response_length, full)
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("RECV: " + hexlify_packets(result))
        except (socket.error, ModbusIOException,
                InvalidMessageReceivedException) as msg:
            self.client.close()
            _logger.debug("Transaction failed. (%s) " % msg)
            last_exception = msg
            result = b''
        return result, last_exception