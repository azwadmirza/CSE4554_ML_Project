    def processIncomingPacket(self, data, callback, unit, **kwargs):
        """
        The new packet processing pattern

        This takes in a new request packet, adds it to the current
        packet stream, and performs framing on it. That is, checks
        for complete messages, and once found, will process all that
        exist.  This handles the case when we read N + 1 or 1 // N
        messages at a time instead of 1.

        The processed and decoded messages are pushed to the callback
        function to process and send.

        :param data: The new packet data
        :param callback: The function to send results to
        :param unit: Process if unit id matches, ignore otherwise (could be a \
        list of unit ids (server) or single unit id(client/server)
        :param single: True or False (If True, ignore unit address validation)
        """
        if not isinstance(unit, (list, tuple)):
            unit = [unit]
        self.addToFrame(data)
        single = kwargs.get("single", False)
        if self.isFrameReady():
            if self.checkFrame():
                if self._validate_unit_id(unit, single):
                    self._process(callback)
                else:
                    _logger.debug("Not a valid unit id - {}, "
                                  "ignoring!!".format(self._header['uid']))
                    self.resetFrame()
        else:
            _logger.debug("Frame - [{}] not ready".format(data))